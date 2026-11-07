insert into public.projects
  (id, title, category, image, problem, solution, architecture, contribution, results, technologies, live_url, github_url, sort_order)
values
  (1, 'English Club: E-Learning Management System', 'Full-Stack', 'English.jpg',
   'Learners needed a unified platform to register, access courses, take quizzes, and track progress—without fragmented tools or insecure access.',
   'Built an end-to-end learning platform with JWT-authenticated REST APIs, role-aware dashboards, and a responsive Next.js frontend for seamless course consumption.',
   'Next.js frontend with NextAuth JWT sessions, RESTful API integration, server-side rendering for performance, and modular page routing for courses, quizzes, and progress tracking.',
   array['Integrated frontend with backend RESTful APIs and ensured smooth data flow', 'Implemented JWT authentication with NextAuth', 'Built user onboarding, course consumption, and progress tracking flows', 'Collaborated with backend team on API contracts and error handling'],
   array['Complete E2E learning flow from registration to progress tracking', 'Secure authenticated access across all user journeys', 'Responsive UI built with TypeScript and Tailwind CSS'],
   array['Next.js', 'TypeScript', 'Tailwind CSS', 'REST APIs', 'JWT', 'NextAuth'], '#', 'https://github.com/BunathPheng', 1),
  (2, 'SmartOps: Automation Platform', 'DevOps', 'Final.png',
   'Manual deployments were slow, error-prone, and lacked traceability from source code to production environments.',
   'Designed a GitOps-first automation platform covering the full deployment lifecycle with CI/CD pipelines, container orchestration, and infrastructure as code.',
   'Jenkins and GitHub Actions for CI, Argo CD for GitOps delivery, Docker/Kubernetes for runtime, Ansible for provisioning, and Prometheus/Grafana for observability.',
   array['Built CI/CD pipelines with Jenkins and GitHub Actions', 'Implemented GitOps workflows with Argo CD', 'Containerized workloads and deployed on Kubernetes', 'Automated infrastructure provisioning with Ansible'],
   array['Automated deployment lifecycle from repo to production', 'Faster, more reliable releases with full traceability', 'Reduced manual intervention and deployment risk'],
   array['Jenkins', 'GitHub Actions', 'Argo CD', 'Docker', 'Kubernetes', 'Ansible', 'Prometheus', 'Grafana'], '#', 'https://github.com/BunathPheng', 2),
  (3, 'Selamounty: Digital Cultural & Educational Hub', 'Platform', 'selamonty.png',
   'Cultural institutions needed a scalable digital platform to deliver rich media content and educational experiences to a global audience.',
   'Delivered backend services and deployment automation for a virtual museum platform with resilient APIs and automated rollouts.',
   'Spring Boot microservices with MySQL persistence, Jenkins CI/CD pipelines, Docker containerization, and Nginx reverse proxy for production traffic.',
   array['Built and maintained Spring Boot API services', 'Set up automated deployment pipelines with Jenkins and Docker', 'Configured Nginx for production traffic routing', 'Ensured reliable rollout for media-rich experiences'],
   array['Scalable platform serving global visitors', 'Automated deployments with minimal downtime', 'Reliable API layer for content delivery'],
   array['Java', 'Spring Boot', 'MySQL', 'Jenkins', 'Docker', 'Nginx'], '#', 'https://github.com/BunathPheng', 3)
on conflict (id) do update set
  title = excluded.title, category = excluded.category, image = excluded.image,
  problem = excluded.problem, solution = excluded.solution, architecture = excluded.architecture,
  contribution = excluded.contribution, results = excluded.results, technologies = excluded.technologies,
  live_url = excluded.live_url, github_url = excluded.github_url, sort_order = excluded.sort_order;

insert into public.skill_groups (category, icon, skills, sort_order) values
  ('DevOps & Cloud', 'cloud', array['Docker', 'Kubernetes', 'Helm', 'Jenkins', 'Argo CD', 'Ansible', 'GitHub Actions', 'Prometheus', 'Grafana'], 1),
  ('Frontend', 'layout', array['React', 'Next.js', 'TypeScript', 'JavaScript', 'HTML', 'CSS', 'Tailwind CSS'], 2),
  ('Backend & Data', 'database', array['Spring Boot', 'Java', 'PostgreSQL', 'MySQL', 'REST APIs', 'JWT'], 3),
  ('Tools & Design', 'tool', array['Git', 'Linux', 'Nginx', 'Figma'], 4);

insert into public.experiences (title, company, location, period, description, technologies, sort_order) values
  ('DevOps Engineer – SmartOps Automation Platform', 'Korea Software HRD Center', 'Phnom Penh, Cambodia', '2025', 'Built an automated platform covering the full deployment lifecycle—from repo to production—using GitOps and CI/CD to simplify, speed up, and de-risk releases.', array['Jenkins', 'GitHub Actions', 'Argo CD', 'Docker', 'Kubernetes', 'Ansible', 'Prometheus', 'Grafana'], 1),
  ('Backend / Platform Engineer – Selamounty', 'Korea Software HRD Center', 'Phnom Penh, Cambodia', '2025', 'Delivered a digital cultural and educational platform with automated deployments, API services, and resilient runtime for global visitors.', array['Java', 'Spring Boot', 'MySQL', 'Jenkins', 'Docker', 'Nginx'], 2),
  ('Front-End Developer – English Club Platform', 'Institute of Science and Technology Advanced Development', 'Phnom Penh, Cambodia', '2024', 'Built an education platform enabling learners to practice English with authenticated user flows and dashboards.', array['Next.js', 'TypeScript', 'JWT', 'REST APIs', 'Tailwind CSS'], 3);

insert into public.education (degree, field, school, period, description, sort_order) values
  ('Bachelor of Computer Science', 'Royal University of Phnom Penh (RUPP)', 'Royal University of Phnom Penh', 'Jan 2022 – Present', 'Comprehensive CS curriculum with focus on software engineering and systems.', 1),
  ('Advanced Course: DevOps', 'Korea Software HRD Center (KSHRD)', 'Korea Software HRD Center', 'Jul – Dec 2025', 'Modern CI/CD, containerization, cloud infrastructure, GitOps with Jenkins, GitHub Actions, Argo CD, Docker, and Kubernetes.', 2),
  ('Basic Course Training', 'Korea Software HRD Center (KSHRD)', 'Korea Software HRD Center', 'Feb – Jul 2025', 'Foundation across Linux, Docker, Git, UI/UX, Java, HTML/CSS/JS, Tailwind CSS, PostgreSQL, and responsive web apps.', 3),
  ('Foundation 2 Generation', 'Institute of Science and Technology Advanced Development (ISTAD)', 'ISTAD', 'Jan 2025 – Present', 'Core software engineering foundations and collaborative projects.', 4);

insert into public.social_links (label, href, sort_order) values
  ('LinkedIn', 'https://www.linkedin.com/in/bunath-pheng-71a41b318', 1),
  ('GitHub', 'https://github.com/BunathPheng', 2),
  ('Telegram', 'https://t.me/pheng_bunath', 3),
  ('Facebook', 'https://web.facebook.com/profile.php?id=100027603155423', 4);

insert into public.nav_items (label, href, sort_order) values
  ('About', '#about', 1), ('Skills', '#skills', 2), ('Projects', '#projects', 3),
  ('Experience', '#experience', 4), ('Education', '#education', 5), ('Contact', '#contact', 6);
