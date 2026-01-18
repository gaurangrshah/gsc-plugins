-- Worklog Seed Data: Tag Taxonomy
-- Canonical tag mappings for consistent tagging and improved search discoverability

INSERT INTO tag_taxonomy (canonical_tag, aliases, category) VALUES
-- Infrastructure
('kubernetes', '{k8s,kube}', 'infrastructure'),
('postgresql', '{postgres,pg,psql}', 'infrastructure'),
('docker', '{container,containers}', 'infrastructure'),
('traefik', '{reverse-proxy}', 'infrastructure'),
('coolify', '{coolify-infra}', 'infrastructure'),
('email', '{smtp,mail,transactional-email,nodemailer}', 'infrastructure'),

-- Development
('python', '{py,python3}', 'development'),
('typescript', '{ts}', 'development'),
('javascript', '{js,node,nodejs}', 'development'),
('testing', '{tests,pytest,jest,vitest}', 'development'),
('react', '{reactjs,react.js}', 'development'),

-- Security
('authentication', '{auth,authn,login}', 'security'),
('authorization', '{authz,permissions,rbac}', 'security'),
('ssl-tls', '{ssl,tls,https,certificate,certs}', 'security'),
('secrets', '{credentials,passwords,keys}', 'security'),

-- Integrations
('gitea', '{git-server}', 'integrations'),
('plane', '{plane.so,plane-so}', 'integrations'),
('webhook', '{webhooks,hooks}', 'integrations'),
('mcp', '{model-context-protocol}', 'integrations'),

-- Agents
('claude-code', '{claude,anthropic}', 'agents'),

-- Operations
('backup', '{backups,restore,recovery}', 'operations'),
('monitoring', '{metrics,observability,logging}', 'operations')
ON CONFLICT (canonical_tag) DO NOTHING;
