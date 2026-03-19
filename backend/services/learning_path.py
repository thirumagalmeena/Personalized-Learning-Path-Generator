from collections import defaultdict, deque
from backend import models
from backend.services.embedding_service import compute_similarity


# -----------------------------
# STEP 1: Get Goal Skills
# -----------------------------
def get_goal_skills(goal_name, db):
    """Get skill names for a given goal by converting IDs to actual skill names"""
    goal = db.query(models.LearningGoal).filter(
        models.LearningGoal.goal_name == goal_name
    ).first()

    if not goal:
        raise ValueError("Goal not found")

    # Split the comma-separated IDs
    skill_ids = [s.strip() for s in goal.target_skills.split(",") if s.strip()]
    
    # Convert IDs to skill names
    skill_names = []
    for id_str in skill_ids:
        try:
            skill_id = int(id_str)
            skill = db.query(models.Skill).filter(
                models.Skill.skill_id == skill_id
            ).first()
            
            if skill:
                skill_names.append(skill.skill_name)
        except ValueError:
            # If it's not a number, maybe it's already a name?
            skill = db.query(models.Skill).filter(
                models.Skill.skill_name == id_str
            ).first()
            if skill:
                skill_names.append(skill.skill_name)
    
    return skill_names


# -----------------------------
# STEP 2: Check if skill is covered (with VAE similarity)
# -----------------------------
def is_skill_covered(user_skills, target_skill, threshold=0.7):
    """
    Check if a target skill is covered by user's existing skills
    through direct match or VAE-based similarity
    """
    target_skill = target_skill.lower()

    for user_skill in user_skills:
        # direct match
        if user_skill.lower() == target_skill:
            return True

        # VAE similarity
        sim = compute_similarity(user_skill, target_skill)

        if sim >= threshold:
            return True

    return False


# -----------------------------
# STEP 3: Compute Skill Gap (with VAE similarity)
# -----------------------------
def compute_skill_gap(user_skills, goal_skills, threshold=0.7):
    """Find skills in goal that user doesn't already have (considering similarities)"""
    gap = []

    for skill in goal_skills:
        if not is_skill_covered(user_skills, skill, threshold):
            gap.append(skill)

    return gap


# -----------------------------
# STEP 4: Expand Prerequisites
# -----------------------------
def expand_with_prerequisites(skill_list, db, user_skills=None):
    """
    Expand skill list to include prerequisites,
    but only if user doesn't already know them
    """
    if user_skills is None:
        user_skills = set()
    else:
        user_skills = set(user_skills)
    
    expanded = set(skill_list)
    stack = list(skill_list)
    
    while stack:
        skill = stack.pop()
        
        # Skip if user already knows this skill
        if skill in user_skills:
            continue

        skill_obj = db.query(models.Skill).filter(
            models.Skill.skill_name == skill
        ).first()

        if not skill_obj:
            continue

        deps = db.query(models.SkillDependency).filter(
            models.SkillDependency.skill_id == skill_obj.skill_id
        ).all()

        for dep in deps:
            prereq_skill = db.query(models.Skill).filter(
                models.Skill.skill_id == dep.prerequisite_skill_id
            ).first()

            if prereq_skill:
                prereq_name = prereq_skill.skill_name
                
                # Only add prerequisite if user doesn't already know it
                if prereq_name not in user_skills:
                    if prereq_name not in expanded:
                        expanded.add(prereq_name)
                        stack.append(prereq_name)

    return list(expanded)


# -----------------------------
# STEP 5: Build Skill Graph
# -----------------------------
def build_skill_graph(skill_names, db):
    """Build dependency graph and calculate in-degrees for topological sorting"""
    graph = defaultdict(list)
    in_degree = defaultdict(int)

    for skill in skill_names:
        skill_obj = db.query(models.Skill).filter(
            models.Skill.skill_name == skill
        ).first()

        if not skill_obj:
            continue

        deps = db.query(models.SkillDependency).filter(
            models.SkillDependency.skill_id == skill_obj.skill_id
        ).all()

        for dep in deps:
            prereq = db.query(models.Skill).filter(
                models.Skill.skill_id == dep.prerequisite_skill_id
            ).first()

            if prereq and prereq.skill_name in skill_names:
                graph[prereq.skill_name].append(skill)
                in_degree[skill] += 1

    # Ensure all skills have an in_degree entry
    for skill in skill_names:
        if skill not in in_degree:
            in_degree[skill] = 0

    return graph, in_degree


# -----------------------------
# STEP 6: Topological Sort
# -----------------------------
def topological_sort(skills, graph, in_degree):
    """Sort skills so prerequisites come before dependent skills"""
    # Create a mutable copy of in_degree
    in_degree_copy = in_degree.copy()
    queue = deque()
    ordered = []
    
    # Initialize queue with nodes that have in-degree 0
    for skill in skills:
        if in_degree_copy[skill] == 0:
            queue.append(skill)
    
    while queue:
        current = queue.popleft()
        ordered.append(current)
        
        # Decrease in-degree for all neighbors
        for neighbor in graph[current]:
            in_degree_copy[neighbor] -= 1
            
            if in_degree_copy[neighbor] == 0:
                queue.append(neighbor)
    
    # Handle cycles by adding any remaining skills
    if len(ordered) != len(skills):
        remaining = set(skills) - set(ordered)
        ordered.extend(list(remaining))
    
    return ordered


# -----------------------------
# STEP 7: Attach Resources
# -----------------------------
def attach_resources(ordered_skills, db):
    """
    Map each skill to a learning resource
    Returns a list of steps with skill and resource details
    """
    steps = []

    for i, skill_name in enumerate(ordered_skills, start=1):
        skill = db.query(models.Skill).filter(
            models.Skill.skill_name == skill_name
        ).first()

        if not skill:
            continue

        # Get the first resource for this skill (you could add logic to pick based on preferences)
        resource = db.query(models.LearningResource).filter(
            models.LearningResource.skill_id == skill.skill_id
        ).first()

        step = {
            "step_number": i,
            "skill": skill.skill_name,
            "skill_id": skill.skill_id,
            "difficulty": skill.difficulty,
            "estimated_learning_hours": skill.estimated_learning_hours,
        }

        if resource:
            step.update({
                "resource_title": resource.resource_title,
                "resource_type": resource.resource_type,
                "estimated_time": resource.estimated_time,
                "url": resource.url
            })
        else:
            step.update({
                "resource_title": None,
                "resource_type": None,
                "estimated_time": None,
                "url": None
            })

        steps.append(step)

    return steps


# -----------------------------
# MAIN PIPELINE FUNCTION
# -----------------------------
def generate_learning_path(user_skills, goal_name, db, similarity_threshold=0.7):
    """
    Main function to generate a personalized learning path with resources.
    
    Args:
        user_skills: List of skill names the user already knows
        goal_name: Name of the target learning goal
        db: Database session
        similarity_threshold: Minimum similarity score to consider a skill covered (default: 0.7)
    
    Returns:
        List of steps with skill and resource details
    """
    # Step 1: Get goal skills
    goal_skills = get_goal_skills(goal_name, db)
    
    # Step 2: Compute gap with VAE similarity matching (db parameter removed)
    gap = compute_skill_gap(user_skills, goal_skills, similarity_threshold)
    
    # If no gap, return empty list
    if not gap:
        return []
    
    # Step 3: Expand with prerequisites (respecting user's existing knowledge)
    expanded = expand_with_prerequisites(gap, db, user_skills)
    
    # Step 4: Build dependency graph
    graph, in_degree = build_skill_graph(expanded, db)
    
    # Step 5: Topologically sort
    ordered_skills = topological_sort(expanded, graph, in_degree)
    
    # Step 6: Filter out skills user already knows (final safety check)
    skills_to_learn = [s for s in ordered_skills if s not in user_skills]
    
    # Step 7: Attach resources to each skill
    steps = attach_resources(skills_to_learn, db)
    
    return steps