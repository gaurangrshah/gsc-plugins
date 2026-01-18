-- Worklog Seed Data: Topic Index
-- Core topics for organizing knowledge base entries

INSERT INTO topic_index (topic_name, summary, key_terms) VALUES
('infrastructure',
 'Servers, containers, networking, deployment, cloud services',
 '{docker,kubernetes,networking,deployment,servers,cloud,traefik,nginx}'),

('development',
 'Coding patterns, tools, workflows, testing, debugging',
 '{code,testing,git,patterns,refactoring,debugging,api,frontend,backend}'),

('security',
 'Authentication, secrets, access control, encryption, compliance',
 '{auth,secrets,ssl,tls,permissions,encryption,oauth,jwt}'),

('operations',
 'Monitoring, maintenance, backups, health checks, incidents',
 '{monitoring,backup,maintenance,health,cron,logging,alerting,incidents}'),

('decisions',
 'Architecture decisions, design choices, trade-offs, ADRs',
 '{adr,architecture,design,decision,tradeoff,evaluation}'),

('integrations',
 'External services, APIs, webhooks, third-party tools',
 '{api,webhook,integration,external,sync,mcp}'),

('agents',
 'AI agents, automation, cross-agent coordination',
 '{agent,automation,claude,assistant,coordination,workflow}'),

('projects',
 'Project-specific context, configurations, conventions',
 '{project,config,setup,conventions,readme}')
ON CONFLICT (topic_name) DO NOTHING;
