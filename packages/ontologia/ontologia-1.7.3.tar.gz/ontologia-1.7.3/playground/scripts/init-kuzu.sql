-- Ontologia Playground KùzuDB Initialization
-- This script sets up the initial graph database schema

-- Create node tables for different entity types
CREATE NODE TABLE Person (
    id STRING,
    name STRING,
    email STRING,
    department STRING,
    level INT64,
    join_date DATE,
    PRIMARY KEY (id)
);

CREATE NODE TABLE Project (
    id STRING,
    name STRING,
    status STRING,
    priority INT64,
    budget DOUBLE,
    start_date DATE,
    PRIMARY KEY (id)
);

CREATE NODE TABLE Skill (
    id STRING,
    name STRING,
    category STRING,
    level STRING,
    PRIMARY KEY (id)
);

CREATE NODE TABLE Company (
    id STRING,
    name STRING,
    industry STRING,
    founded DATE,
    size STRING,
    PRIMARY KEY (id)
);

CREATE NODE TABLE Department (
    id STRING,
    name STRING,
    manager STRING,
    budget DOUBLE,
    PRIMARY KEY (id)
);

-- Create relationship tables
CREATE REL TABLE WORKS_ON (
    FROM Person TO Project,
    role STRING,
    since DATE
);

CREATE REL TABLE HAS_SKILL (
    FROM Person TO Skill,
    proficiency INT64
);

CREATE REL TABLE MANAGES (
    FROM Person TO Department,
    since DATE
);

CREATE REL TABLE BELONGS_TO (
    FROM Person TO Department,
    since DATE
);

CREATE REL TABLE PART_OF (
    FROM Project TO Department,
    budget_allocation DOUBLE
);

CREATE REL TABLE LOCATED_IN (
    FROM Department TO Company,
    floor INT64
);

-- Create indexes for better performance
CREATE INDEX person_name_idx ON Person(name);
CREATE INDEX person_department_idx ON Person(department);
CREATE INDEX project_status_idx ON Project(status);
CREATE INDEX project_priority_idx ON Project(priority);
CREATE INDEX skill_category_idx ON Skill(category);
CREATE INDEX company_industry_idx ON Company(industry);

-- Insert sample data for demonstration

-- Sample companies
INSERT INTO Company VALUES
('company1', 'TechCorp', 'Technology', '2010-01-15', 'Large'),
('company2', 'HealthInc', 'Healthcare', '2015-06-20', 'Medium'),
('company3', 'FinanceCo', 'Finance', '2008-03-10', 'Large');

-- Sample departments
INSERT INTO Department VALUES
('dept1', 'Engineering', 'person3', 1000000.0),
('dept2', 'Product', 'person3', 500000.0),
('dept3', 'Design', 'person5', 300000.0),
('dept4', 'Marketing', 'person8', 400000.0);

-- Link departments to company
INSERT INTO LOCATED_IN VALUES
('dept1', 'company1', 3),
('dept2', 'company1', 2),
('dept3', 'company1', 4),
('dept4', 'company1', 1);

-- Sample people
INSERT INTO Person VALUES
('person1', 'Alice Johnson', 'alice@techcorp.com', 'Engineering', 5, '2020-01-15'),
('person2', 'Bob Smith', 'bob@techcorp.com', 'Engineering', 4, '2020-03-20'),
('person3', 'Carol Davis', 'carol@techcorp.com', 'Product', 6, '2019-11-10'),
('person4', 'David Wilson', 'david@techcorp.com', 'Product', 3, '2021-02-01'),
('person5', 'Eve Brown', 'eve@techcorp.com', 'Design', 5, '2020-07-15'),
('person6', 'Frank Miller', 'frank@techcorp.com', 'Engineering', 4, '2021-01-10'),
('person7', 'Grace Lee', 'grace@techcorp.com', 'Design', 3, '2021-09-05'),
('person8', 'Henry Taylor', 'henry@techcorp.com', 'Product', 5, '2020-05-20');

-- Link people to departments
INSERT INTO BELONGS_TO VALUES
('person1', 'dept1', '2020-01-15'),
('person2', 'dept1', '2020-03-20'),
('person3', 'dept2', '2019-11-10'),
('person4', 'dept2', '2021-02-01'),
('person5', 'dept3', '2020-07-15'),
('person6', 'dept1', '2021-01-10'),
('person7', 'dept3', '2021-09-05'),
('person8', 'dept2', '2020-05-20');

-- Management relationships
INSERT INTO MANAGES VALUES
('person3', 'dept2', '2019-11-10'),
('person5', 'dept3', '2020-07-15');

-- Sample projects
INSERT INTO Project VALUES
('project1', 'Mobile App Development', 'active', 1, 500000.0, '2023-01-01'),
('project2', 'Website Redesign', 'planning', 2, 150000.0, '2023-06-01'),
('project3', 'Data Platform', 'active', 1, 750000.0, '2023-03-15'),
('project4', 'Customer Portal', 'completed', 2, 200000.0, '2022-09-01'),
('project5', 'Analytics Dashboard', 'active', 3, 100000.0, '2023-07-01');

-- Link projects to departments
INSERT INTO PART_OF VALUES
('project1', 'dept1', 300000.0),
('project2', 'dept3', 100000.0),
('project3', 'dept1', 500000.0),
('project4', 'dept2', 150000.0),
('project5', 'dept2', 100000.0);

-- Sample skills
INSERT INTO Skill VALUES
('skill1', 'Python', 'Programming', 'Advanced'),
('skill2', 'JavaScript', 'Programming', 'Intermediate'),
('skill3', 'UI Design', 'Design', 'Advanced'),
('skill4', 'Data Analysis', 'Analytics', 'Advanced'),
('skill5', 'Project Management', 'Management', 'Intermediate'),
('skill6', 'SQL', 'Database', 'Intermediate'),
('skill7', 'React', 'Programming', 'Intermediate'),
('skill8', 'Machine Learning', 'Analytics', 'Advanced'),
('skill9', 'Leadership', 'Management', 'Advanced'),
('skill10', 'Communication', 'Soft Skills', 'Advanced');

-- Work assignments
INSERT INTO WORKS_ON VALUES
('person1', 'project1', 'Lead Developer', '2023-01-01'),
('person2', 'project1', 'Developer', '2023-02-01'),
('person3', 'project2', 'Manager', '2023-06-01'),
('person4', 'project2', 'Designer', '2023-07-01'),
('person5', 'project2', 'Lead Designer', '2023-06-15'),
('person1', 'project3', 'Architect', '2023-03-15'),
('person6', 'project3', 'Developer', '2023-04-01'),
('person8', 'project3', 'Product Owner', '2023-03-20'),
('person3', 'project4', 'Manager', '2022-09-01'),
('person5', 'project4', 'Designer', '2022-10-01'),
('person7', 'project5', 'Designer', '2023-07-01'),
('person8', 'project5', 'Analyst', '2023-07-15');

-- Skill assignments
INSERT INTO HAS_SKILL VALUES
('person1', 'skill1', 5),
('person1', 'skill4', 4),
('person1', 'skill6', 4),
('person2', 'skill1', 4),
('person2', 'skill2', 3),
('person2', 'skill7', 3),
('person3', 'skill4', 5),
('person3', 'skill5', 4),
('person4', 'skill3', 4),
('person4', 'skill5', 3),
('person5', 'skill3', 5),
('person5', 'skill2', 3),
('person6', 'skill1', 4),
('person6', 'skill6', 3),
('person7', 'skill3', 4),
('person7', 'skill2', 2),
('person8', 'skill4', 5),
('person8', 'skill8', 4),
('person8', 'skill5', 4),
('person3', 'skill9', 5),
('person3', 'skill10', 5);

-- Create some useful views for common queries

-- View for people with their skills
CREATE VIEW PeopleWithSkills AS
MATCH (p:Person)-[h:HAS_SKILL]->(s:Skill)
RETURN
    p.id AS person_id,
    p.name AS person_name,
    p.department AS department,
    p.level AS level,
    s.id AS skill_id,
    s.name AS skill_name,
    s.category AS skill_category,
    h.proficiency AS proficiency;

-- View for projects with team members
CREATE VIEW ProjectTeams AS
MATCH (p:Person)-[w:WORKS_ON]->(pr:Project)
RETURN
    pr.id AS project_id,
    pr.name AS project_name,
    pr.status AS status,
    pr.priority AS priority,
    p.id AS person_id,
    p.name AS person_name,
    p.department AS department,
    w.role AS role,
    w.since AS since;

-- View for department hierarchy
CREATE VIEW DepartmentStructure AS
MATCH (d:Department)<-[:BELONGS_TO]-(p:Person)
RETURN
    d.id AS dept_id,
    d.name AS dept_name,
    d.budget AS budget,
    COUNT(p.id) AS employee_count,
    COLLECT(p.name) AS employees;

-- View for skill distribution
CREATE VIEW SkillDistribution AS
MATCH (p:Person)-[h:HAS_SKILL]->(s:Skill)
RETURN
    s.name AS skill_name,
    s.category AS category,
    COUNT(p.id) AS people_count,
    AVG(h.proficiency) AS avg_proficiency;

-- View for project status by department
CREATE VIEW ProjectStatusByDept AS
MATCH (d:Department)<-[:PART_OF]-(pr:Project)
RETURN
    d.name AS department,
    pr.status AS status,
    COUNT(pr.id) AS project_count,
    SUM(pr.budget) AS total_budget;

-- Create stored procedures for common operations

-- Procedure to find experts in a skill
CREATE MACRO find_experts(skill_name STRING) AS
MATCH (p:Person)-[h:HAS_SKILL]->(s:Skill)
WHERE s.name = skill_name
RETURN p.name AS expert_name, p.department, h.proficiency
ORDER BY h.proficiency DESC, p.level DESC
LIMIT 5;

-- Procedure to find people working on active projects
CREATE MACRO find_active_workers() AS
MATCH (p:Person)-[w:WORKS_ON]->(pr:Project)
WHERE pr.status = 'active'
RETURN DISTINCT p.name AS worker, p.department, COLLECT(pr.name) AS active_projects;

-- Procedure to find skill gaps in departments
CREATE MACRO find_skill_gaps(dept_name STRING) AS
MATCH (d:Department {name: dept_name})<-[:BELONGS_TO]-(p:Person)
WITH d, COLLECT(p) AS dept_people
MATCH (s:Skill)
WHERE NOT EXISTS ((dept_people)-[:HAS_SKILL]->(s))
RETURN s.name AS missing_skill, s.category AS category;

-- Procedure to calculate project complexity
CREATE MACRO project_complexity(project_id STRING) AS
MATCH (pr:Project {id: project_id})<-[:WORKS_ON]-(p:Person)
WITH pr, COUNT(p) AS team_size, COLLECT(p.level) AS team_levels
MATCH (pr:Project {id: project_id})<-[:WORKS_ON]-(p:Person)-[:HAS_SKILL]->(s:Skill)
WITH pr, team_size, team_levels, COUNT(DISTINCT s.id) AS skill_count
RETURN
    pr.name AS project_name,
    team_size,
    AVG(team_levels) AS avg_experience,
    skill_count,
    (team_size * skill_count) AS complexity_score;

-- Procedure to recommend collaboration
CREATE MACRO recommend_collaboration(person_id STRING) AS
MATCH (p1:Person {id: person_id})-[:HAS_SKILL]->(s1:Skill)<-[:HAS_SKILL]-(p2:Person)
WHERE p1.id <> p2.id
AND NOT EXISTS ((p1)-[:WORKS_ON]->(:Project)<-[:WORKS_ON]-(p2))
RETURN p2.name AS potential_collaborator,
       p2.department AS department,
       COLLECT(s1.name) AS shared_skills,
       COUNT(s1) AS shared_skill_count
ORDER BY shared_skill_count DESC, p2.level DESC
LIMIT 3;

-- Print initialization summary
COPY (
    SELECT
        'KùzuDB Graph Database Initialized Successfully' as status,
        COUNT(*) as person_count
    FROM Person
    UNION ALL
    SELECT
        'Projects Created',
        COUNT(*)
    FROM Project
    UNION ALL
    SELECT
        'Skills Defined',
        COUNT(*)
    FROM Skill
    UNION ALL
    SELECT
        'Work Relationships Created',
        COUNT(*)
    FROM WORKS_ON
    UNION ALL
    SELECT
        'Skill Relationships Created',
        COUNT(*)
    FROM HAS_SKILL
) TO STDOUT (HEADER=true, DELIMITER=',');
