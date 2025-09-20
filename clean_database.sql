-- Clean up fake data and prepare for real data
-- Delete all fake energy usage records
DELETE FROM energy_usage WHERE user_id IN ('user-alice', 'user-bob', 'user-carol', 'user-david', 'user-eve');

-- Delete fake users
DELETE FROM users WHERE user_id IN ('user-alice', 'user-bob', 'user-carol', 'user-david', 'user-eve');

-- Keep the teams but update them to be more realistic
UPDATE teams SET 
    team_name = 'Engineering',
    organization = 'Your Company'
WHERE team_id = 'team-engineering';

UPDATE teams SET 
    team_name = 'Marketing',
    organization = 'Your Company'
WHERE team_id = 'team-marketing';

UPDATE teams SET 
    team_name = 'Sales',
    organization = 'Your Company'
WHERE team_id = 'team-sales';

UPDATE teams SET 
    team_name = 'Research',
    organization = 'Your Company'
WHERE team_id = 'team-research';

-- Add a real user for testing
INSERT INTO users (user_id, email, team_id) 
VALUES ('real-user-1', 'you@yourcompany.com', 'team-engineering')
ON CONFLICT (user_id) DO NOTHING;
