# Mistakes Most Vibe Coders Fall Into

Research date: 2026-06-25

This note summarizes recurring mistakes made when people use AI coding tools to build apps, products, websites, automations, content workflows, and internal tools quickly. It covers common practice mistakes as well as deployment, UI/UX, backend design, security, testing, performance, data, product quality, and maintenance.

## Executive Summary

Vibe coding is strongest when it is treated as a fast exploration and prototyping workflow. It becomes risky when the generated output is mistaken for a finished product, a finished business decision, or a finished operating process. The common pattern is simple: the work looks complete because the visible happy path works, but the hidden parts are unfinished: user validation, requirements, authorization, data ownership, error handling, backups, observability, performance budgets, dependency review, UX edge cases, support plans, and business constraints.

The most dangerous mistakes are:

1. Shipping before auditing what the AI actually built.
2. Trusting UI-level checks instead of server-side authorization.
3. Deploying with weak environment separation, no rollback, and no tested backup.
4. Adding dependencies without understanding why they exist.
5. Optimizing for visual polish before the core flow, data model, and backend are stable.
6. Testing only the demo path.
7. Ignoring performance until the app is already slow, costly, or both.
8. Prompting vaguely, then blaming the tool for vague output.
9. Skipping user research because a generated interface feels convincing.
10. Accumulating features faster than the builder can understand, support, or maintain them.
11. Treating testing as "click around once" instead of a repeated product, UX, security, and release habit.

## Sources Used

- TechRadar, ["Vibe coding guide: How to transition from AI generation to live deployment"](https://www.techradar.com/pro/vibe-coding-guide-how-to-transition-from-ai-generation-to-live-deployment), 2026.
- Convex, ["6 Steps Before Taking your Vibe-coded App to Production"](https://stack.convex.dev/vibe-coding-to-production).
- OWASP, ["Top Ten Web Application Security Risks"](https://owasp.org/www-project-top-ten/).
- OWASP, ["API Security Project / API Security Top 10 2023"](https://owasp.org/www-project-api-security/).
- Google web.dev, ["Web Vitals"](https://web.dev/articles/vitals).
- Nielsen Norman Group, ["10 Usability Heuristics for User Interface Design"](https://www.nngroup.com/articles/ten-usability-heuristics/).
- PromptHub, ["How to vibe code with no-code tools: Prompting tips and how to troubleshoot"](https://www.prompthub.us/blog/how-to-vibe-code-with-no-code-tools-prompting-tips-and-how-to-troubleshoot), 2025.
- Supabase, ["Vibe Coding: Best Practices for Prompting"](https://supabase.com/blog/vibe-coding-best-practices-for-prompting), 2025.
- Kaspersky, ["Security risks of vibe coding and LLM assistants for developers"](https://www.kaspersky.com/blog/vibe-coding-2025-risks/54584/), 2025.
- Endor Labs, ["The Most Common Security Vulnerabilities in AI-Generated Code"](https://www.endorlabs.com/learn/the-most-common-security-vulnerabilities-in-ai-generated-code), 2025.
- Georgetown CSET, ["Cybersecurity Risks of AI-Generated Code"](https://cset.georgetown.edu/publication/cybersecurity-risks-of-ai-generated-code/).

## Common Practice Mistakes Beyond Code

These are the habits that make vibe-coded work fail even when the code is not the immediate problem.

### 1. Starting With a Vibe Instead of a Clear Problem

The mistake is opening the builder with "make me an app like X" before defining the real user, real pain, real workflow, and success criteria.

What usually goes wrong:

- The output imitates a category instead of solving a specific problem.
- The product becomes a bundle of familiar screens: dashboard, profile, settings, analytics, chat, admin.
- The builder keeps adding features because there is no strong definition of what should not exist.
- The final product feels generic even if it looks polished.

Better practice:

- Write a one-paragraph problem statement before prompting.
- Define the target user, their current workaround, and what "done" means.
- List the one workflow that must feel excellent.
- Keep a "not building yet" list to resist feature drift.

### 2. Confusing Speed With Validation

The mistake is thinking, "I built it in two days, so the idea is proven."

Fast building proves that a tool can generate something. It does not prove that users want it, trust it, understand it, or will pay for it.

What usually goes wrong:

- Builders skip interviews, usability tests, and pricing validation.
- Friends praise the demo but never become users.
- The product solves a problem that is annoying but not valuable.
- A landing page, brand, or dashboard gets polished before demand is tested.

Better practice:

- Talk to users before and after building.
- Test a clickable prototype or rough demo with real users.
- Measure behavior, not compliments.
- Ask what users would stop using if your product worked.
- Validate willingness to pay before building billing, admin, and reporting features.

### 3. Prompting With Assumptions Hidden in Your Head

The mistake is giving the AI a short instruction while expecting it to infer the product context, tone, constraints, business rules, audience, and edge cases.

PromptHub's guidance emphasizes structured prompts with context, task, details, requirements, constraints, and "don'ts." This matters because the model only sees what you give it.

What usually goes wrong:

- The AI chooses the wrong stack, layout, tone, or workflow.
- The AI edits unrelated files because the scope was vague.
- The AI adds features the builder never wanted.
- The builder spends more time correcting output than defining the request.

Better practice:

- Include context, task, constraints, acceptance criteria, and non-goals.
- Tell the AI what not to change.
- Ask for one feature or one decision at a time.
- Ask the AI to repeat its plan before implementation for risky work.
- Keep reusable prompts for recurring tasks: UI polish, accessibility review, security review, performance review, and release checklist.

### 4. Letting the AI Become the Product Manager

The mistake is letting the AI decide the roadmap, information architecture, onboarding, pricing model, roles, permissions, and settings structure.

What usually goes wrong:

- The app gets standard SaaS furniture whether it needs it or not.
- Screens exist because the AI expects them, not because users need them.
- User roles are vague.
- The product becomes hard to explain in one sentence.

Better practice:

- Own the product decisions yourself.
- Ask the AI for options, tradeoffs, and risks instead of one automatic answer.
- Decide the core workflow before generating UI.
- Keep a short product brief and update it as decisions change.

### 5. Over-Polishing the First Version

The mistake is spending early energy on animations, gradients, icons, landing pages, brand copy, and decorative UI before the product's core job works.

What usually goes wrong:

- The builder gets emotionally attached to a weak direction because it looks good.
- UX problems are hidden under visual polish.
- The product becomes harder to change after the wrong surfaces are polished.
- Users admire the interface but fail the task.

Better practice:

- Make the core workflow useful before making it beautiful.
- Use plain UI while validating structure.
- Polish only the screens users must trust.
- Treat visual design as a multiplier, not a substitute for product clarity.

### 6. Copying Competitors Without Understanding Their Constraints

The mistake is asking AI to clone the visible surface of another product without knowing the business model, compliance burden, support process, data model, or team behind it.

What usually goes wrong:

- The product inherits complexity without inheriting the reason for that complexity.
- The builder copies enterprise UX for a simple consumer workflow.
- Pricing, onboarding, and permissions are copied from products with different customers.
- The result feels familiar but strategically weak.

Better practice:

- Study competitors for user expectations, not as a blueprint.
- Identify which conventions matter and which ones are baggage.
- Ask what your product can remove, not only what it can copy.
- Document where you intentionally differ.

### 7. Ignoring Distribution Until After the Build

The mistake is building a product first and asking "how do I get users?" later.

What usually goes wrong:

- The product has no clear audience or channel.
- The feature set does not match the buying trigger.
- The builder needs content, SEO, partnerships, sales, or community work that should have started earlier.
- The product launches to silence.

Better practice:

- Define the acquisition channel before building.
- Shape the product around how users will discover and try it.
- Build share loops, invite flows, SEO pages, or onboarding only when they match the channel.
- Start collecting interested users before the product is complete.

### 8. No Taste Filter

The mistake is accepting generated UI, copy, icons, names, emails, and onboarding text because they are "good enough."

What usually goes wrong:

- The product sounds generic.
- The UI is full of repeated sections, vague headings, and filler microcopy.
- Brand tone changes from page to page.
- Users feel the product is low-trust even when the functionality is real.

Better practice:

- Edit generated copy like a human wrote a rushed first draft.
- Remove filler claims such as "seamless," "powerful," "intuitive," and "revolutionary" unless they are proven.
- Use specific labels and concrete promises.
- Build a small voice and UI style guide.
- Compare every screen against the user's actual next decision.

### 9. Treating AI Output as Authority

The mistake is assuming the AI is correct because it sounds confident.

What usually goes wrong:

- Incorrect technical claims become architecture.
- Fake business assumptions become roadmap.
- Legal, tax, medical, financial, or compliance advice is accepted without expert review.
- The builder stops learning because the AI always has an answer.

Better practice:

- Ask for sources when facts matter.
- Verify claims against primary documentation.
- Use experts for high-stakes areas.
- Ask the AI for uncertainty, alternatives, and failure modes.
- Keep ownership of final decisions.

### 10. Changing Too Many Variables at Once

The mistake is modifying product scope, design style, database structure, auth, pricing, and deployment in the same session.

What usually goes wrong:

- The builder cannot tell which change caused the new problem.
- The AI loses context or overwrites previous decisions.
- Rollback becomes painful.
- The product direction changes with every prompt.

Better practice:

- Work in small loops: decide, generate, review, test, commit.
- Keep separate sessions for planning, design, backend, content, and debugging when the context gets crowded.
- Save known-good versions.
- Summarize decisions after each major milestone.

### 11. Not Building an Operating Habit

The mistake is thinking the project ends at launch.

What usually goes wrong:

- Support messages, bug reports, refunds, privacy requests, abuse, and downtime feel surprising.
- No one knows how often to review logs, costs, backups, analytics, or feedback.
- The product slowly degrades because no maintenance rhythm exists.

Better practice:

- Create a weekly operating checklist.
- Review user feedback, errors, costs, security updates, and analytics.
- Keep a simple issue backlog.
- Schedule dependency and backup checks.
- Decide what metrics would make you pause feature work and fix the foundation.

### 12. Building Alone for Too Long

The mistake is staying in a private AI loop without user critique, peer review, or expert feedback.

What usually goes wrong:

- The builder loses perspective.
- Obvious UX issues survive because no one new has tried the flow.
- Security and data risks go unnoticed.
- The product reflects the builder's mental model, not the user's world.

Better practice:

- Show rough versions early.
- Ask users to complete tasks without guidance.
- Get a technical review before handling real data or payments.
- Get a design review before polishing the interface.
- Keep a small group of honest testers who are not afraid to say, "I do not get it."

## 1. Treating a Prototype as Production-Ready

### The Mistake

The app works in the browser, so the builder assumes it is ready to publish. This skips the gap between "demo complete" and "production dependable."

### Why It Happens

AI tools are very good at creating convincing first versions. A smooth demo can hide weak structure: loose data models, missing access rules, fragile API routes, and undocumented assumptions.

### What Breaks

- Users hit flows that were never tested.
- Data gets corrupted because real usage is messier than the prompt.
- A platform deploy goes live without rollback or staging.
- Costs spike when a viral feature triggers expensive API or hosting usage.
- The builder cannot explain how the app works well enough to debug it.

### How to Avoid It

- Audit every page, API route, database table, background job, and integration.
- Write down the core architecture in plain language.
- Separate prototype, staging, and production environments.
- Add version control before serious iteration.
- Add backups, restore testing, logs, and error alerts before launch.
- Freeze new features until security and data ownership are reviewed.

## 2. Skipping Threat Modeling and Security Review

### The Mistake

Many vibe-coded apps ask, "Does this feature work?" but not, "Who can abuse this feature?"

### Why It Happens

Security is mostly invisible when the app is behaving normally. AI-generated code may also look clean while still missing critical protections.

### What Breaks

- Broken access control lets users read or modify other users' data.
- API routes check whether a user is logged in but not whether they own the record.
- Secrets leak into client code, logs, screenshots, commits, or deployed bundles.
- CORS, authentication, and database permissions are left in permissive demo settings.
- File upload, webhook, and admin routes become attack surfaces.

OWASP lists broken access control as a major web application risk, and the OWASP API Top 10 puts broken object-level authorization at the top of API risks. These are exactly the kinds of mistakes that appear when an app is assembled quickly from generated routes and screens.

### How to Avoid It

- Require authentication and authorization on every server-side route.
- Check ownership for every object ID supplied by the user.
- Keep secrets in environment variables, never in browser-exposed code.
- Validate all input server-side, even when the UI already validates it.
- Use parameterized queries or ORM-safe query APIs.
- Add rate limits for login, search, uploads, checkout, AI calls, and public endpoints.
- Review logs to ensure tokens, passwords, medical data, payment data, and private messages are never printed.
- Run dependency and secret scanners before deployment.

## 3. Trusting the Frontend Too Much

### The Mistake

The UI hides a button, disables a field, or blocks a route, so the builder assumes the action is protected.

### Why It Happens

AI-generated apps often place business logic in components because that is the fastest way to make the demo work.

### What Breaks

- A user can call the API directly and bypass the UI.
- Admin-only actions are protected by a client-side role check.
- Prices, discounts, permissions, or quotas can be modified from the browser.
- Deleted UI features leave old backend endpoints still active.

### How to Avoid It

- Treat the frontend as untrusted.
- Put permissions, pricing, quota, and ownership checks on the backend.
- Keep authorization logic close to the data operation.
- Delete unused API routes when features are removed.
- Add tests that call APIs directly without the UI.

## 4. Poor Backend and Data Modeling

### The Mistake

The app grows around whatever schema the AI created first.

### Why It Happens

Early prompts usually describe screens and features, not domain boundaries, data lifecycles, or migration strategy.

### What Breaks

- Tables have vague names and overlapping responsibilities.
- User data lacks ownership fields or tenant boundaries.
- One record stores unrelated concepts because it was convenient for the first screen.
- Deleting a user leaves orphaned data.
- The app cannot support teams, roles, audit history, billing, or reporting without painful rewrites.

### How to Avoid It

- Model the domain before adding more screens.
- Define ownership: who created it, who can see it, who can edit it, who can delete it.
- Add timestamps, status fields, and audit fields where the business will need them.
- Plan migrations instead of manually editing production data.
- Use database constraints for invariants that must never be broken.
- Test concurrent actions, such as two users editing or purchasing the same resource.

## 5. Unverified Dependencies and Hallucinated Packages

### The Mistake

The builder accepts every package the AI suggests.

### Why It Happens

AI tools often optimize for speed and may import packages that are outdated, unnecessary, vulnerable, or even nonexistent. Kaspersky and Endor Labs both highlight dependency risks in AI-assisted development, including insecure packages and hallucinated dependencies.

### What Breaks

- The app carries multiple libraries for the same job.
- Vulnerable packages enter the project unnoticed.
- A malicious package with a plausible name gets installed.
- Bundle size grows because heavy libraries are used for small tasks.
- Upgrades become scary because no one knows which dependency matters.

### How to Avoid It

- Ask why each new dependency is needed.
- Prefer standard library or existing project utilities when reasonable.
- Check package age, maintainers, download patterns, license, and open issues.
- Run `npm audit`, `pnpm audit`, `pip-audit`, `safety`, `bundler-audit`, or the equivalent for the stack.
- Remove unused dependencies after large AI-generated changes.
- Pin versions intentionally and use a lockfile.

## 6. Weak Deployment Discipline

### The Mistake

The app is deployed directly from the builder or local machine with no clear release process.

### Why It Happens

One-click deployment makes sharing easy. It also makes it easy to skip the operational basics.

### What Breaks

- Staging and production point to the same database.
- A test change affects real users.
- Rollback is impossible or manual.
- Environment variables differ between local, staging, and production.
- Background jobs, cron tasks, and webhooks behave differently after deploy.
- The app depends on a platform-specific feature that makes migration difficult.

### How to Avoid It

- Use separate projects, databases, API keys, and storage buckets for staging and production.
- Require a checklist before production deploys.
- Keep infrastructure settings documented.
- Test migrations against a staging copy.
- Add health checks and smoke tests.
- Confirm the app can be rebuilt from the repository, not only from the AI platform.
- Know the exit plan if the hosting platform changes pricing, limits, or export support.

## 7. No Backup, Restore, or Rollback Plan

### The Mistake

The builder assumes the platform keeps things safe.

### Why It Happens

Backups feel like a future problem until the first accidental deletion, broken migration, or compromised account.

### What Breaks

- A bad AI-generated command wipes production data.
- The only backup is too old or incomplete.
- Restores fail because they were never tested.
- The app has logs but no way to reconstruct what changed.

### How to Avoid It

- Automate database backups.
- Store backups away from the production account.
- Test restoring to a separate environment.
- Keep migration rollback notes.
- Add soft deletes or audit trails for important user data.
- Limit production write access for AI agents and local scripts.

## 8. Testing Only the Happy Path

### The Mistake

The builder tests the exact flow they prompted for, sees it work once, and moves on. This is one of the most common vibe-coding traps because generated apps often look convincing before they are resilient.

### Why It Happens

AI tools produce impressive happy paths. Real users create unhappy paths. Also, many vibe coders think of testing as a code activity only, when it is really a product practice: you test the idea, the UX, the copy, the data, the security model, the deployment, and the recovery plan.

### What Breaks

- Empty states look broken.
- Slow networks create duplicate submissions.
- Invalid input crashes pages.
- Permission errors reveal internal details.
- Race conditions appear under two-user scenarios.
- Payment, email, webhook, and file-upload failures leave partial state.
- Users misunderstand the product even though the code works.
- The app passes a local demo but fails on mobile, real data, or staging.
- A fix for one bug quietly breaks another flow.

### How to Avoid It

Think in layers:

- Product testing: Before building deeply, test whether the problem is real, painful, and frequent enough. A working app does not prove a useful product.
- Usability testing: Watch someone complete the main task without coaching. Note where they pause, misread labels, or click the wrong thing.
- Content testing: Check whether headings, button labels, errors, onboarding text, and emails make sense to a real user.
- Functional testing: Test the main flow, alternate flows, empty states, loading states, error states, cancellation, retry, and undo.
- Permission testing: Log in as different roles and confirm each user can access only what they should.
- API testing: Call important endpoints directly, without the UI, to confirm backend checks actually exist.
- Data testing: Use realistic messy data, large lists, duplicate names, missing fields, long text, non-English names, time zones, and old records.
- Mobile testing: Test real small-screen layouts, touch targets, keyboard behavior, modals, tables, and forms.
- Accessibility testing: Use keyboard-only navigation, screen-reader checks, visible focus states, labels, and contrast checks.
- Security testing: Run secret scans, dependency scans, auth checks, rate-limit checks, upload checks, and basic OWASP-style review.
- Performance testing: Measure load time, interaction delay, layout shift, query speed, bundle size, and expensive API usage.
- Deployment testing: Smoke test staging before production, then smoke test production after release.
- Recovery testing: Restore a backup into a separate environment and verify the app can run from restored data.
- Regression testing: When fixing one issue, retest the related flow and the flows near it.

Minimum testing habit:

- Write down the top five flows that must never break.
- For each flow, test success, failure, empty state, permission denial, and slow network.
- Add automated tests for business rules and critical API behavior.
- Add end-to-end tests only for the flows where a break would seriously hurt users or revenue.
- Before every launch, run a short manual checklist on staging.
- After every launch, run a production smoke test.
- Ask the AI to generate test ideas, but do not let it be the only tester.

Common testing mistake by vibe coders:

- They ask the AI, "Test this app," which often leads to shallow checks.
- Better prompt: "Create a test plan for this app covering happy path, edge cases, permissions, bad input, mobile UX, accessibility, performance, deployment, data recovery, and abuse cases. Prioritize the top 20 tests before launch."

Another useful prompt:

```text
Act as a skeptical QA lead. Read this feature and list ways it can fail for real users.
Include invalid inputs, slow network, duplicate clicks, role/permission issues, empty data,
large data, mobile layout, accessibility, security, and rollback concerns.
Do not write code yet. First produce a prioritized test matrix.
```

## 9. UI/UX That Looks Finished but Feels Confusing

### The Mistake

The app gets a polished surface before the user journey is clear.

### Why It Happens

AI tools can quickly create attractive layouts, gradients, cards, and animations. They are less reliable at understanding the user's job, context, language, and stress.

### What Breaks

- The page looks nice but users do not know what to do next.
- Important actions are hidden below decorative sections.
- Empty states, errors, and loading states are generic or missing.
- Forms ask for too much too early.
- Navigation changes from screen to screen.
- Mobile layouts overlap, truncate, or bury primary actions.
- The interface uses internal jargon instead of user language.

Nielsen Norman Group's usability heuristics are still a useful baseline: show system status, use familiar language, preserve user control, stay consistent, prevent errors, reduce memory load, support efficient use, keep design minimal, help users recover from errors, and provide help when needed.

### How to Avoid It

- Define the primary user and their top three jobs.
- Make the first screen useful, not merely impressive.
- Use consistent navigation, labels, button styles, and form patterns.
- Design empty, loading, success, error, and permission states.
- Put destructive actions behind confirmation and recovery.
- Test on mobile early.
- Watch someone use the app without explaining it.

## 10. Accessibility as an Afterthought

### The Mistake

The UI is considered done because it looks good to the builder.

### Why It Happens

Generated UI often misses semantic HTML, keyboard behavior, focus states, labels, contrast, and screen-reader details unless explicitly requested and verified.

### What Breaks

- Forms cannot be used with assistive technology.
- Modals trap users or fail to trap focus when they should.
- Buttons are built from clickable `div` elements.
- Color-only status indicators exclude some users.
- Keyboard users cannot complete core workflows.

### How to Avoid It

- Use semantic HTML and accessible component libraries.
- Label every form input.
- Preserve visible focus states.
- Check color contrast.
- Test keyboard-only navigation.
- Add `aria-*` only when native HTML is not enough.
- Run automated checks, then manually test the main flow.

## 11. Performance and Cost Blind Spots

### The Mistake

The app is optimized only after it becomes slow or expensive.

### Why It Happens

Generated code often favors simple implementation over efficient data access, caching, bundle size, or API cost control.

### What Breaks

- Pages fetch too much data.
- Components re-render excessively.
- Images are unoptimized.
- Search and dashboard screens become slow with real data.
- AI calls run repeatedly or with oversized prompts.
- Database queries lack indexes.
- Hosting, database, storage, email, map, or LLM bills spike.

Google's Web Vitals provide useful user-facing performance targets: Largest Contentful Paint for loading, Interaction to Next Paint for responsiveness, and Cumulative Layout Shift for visual stability.

### How to Avoid It

- Measure before and after major changes.
- Add indexes for common filters and joins.
- Paginate lists and reports.
- Cache expensive reads where freshness allows it.
- Debounce search and autosave.
- Optimize images and avoid unnecessary client-side JavaScript.
- Set spending limits and usage alerts for paid APIs.
- Log AI token usage and cache repeated AI results.

## 12. State Management Sprawl

### The Mistake

State is copied into many components until no one knows the source of truth.

### Why It Happens

AI-generated UI often solves each screen locally. That works until flows cross screens or users edit the same data from multiple places.

### What Breaks

- The UI shows stale data after updates.
- Filters, pagination, and selected records reset unexpectedly.
- Optimistic updates disagree with server truth.
- Bugs appear only after navigation or refresh.
- The app has duplicate validation logic in several components.

### How to Avoid It

- Define server state, URL state, form state, and local UI state separately.
- Use a consistent data-fetching library or framework pattern.
- Keep server truth authoritative.
- Put shared validation in one place.
- Make URL parameters represent shareable view state when appropriate.

## 13. Error Handling That Helps Nobody

### The Mistake

Errors are either swallowed silently or shown as raw technical messages.

### Why It Happens

The happy path gets generated first, and error states are usually underspecified.

### What Breaks

- Users retry dangerous actions and create duplicates.
- Support cannot diagnose problems.
- Stack traces leak implementation details.
- Failed payments, uploads, or submissions leave unclear state.

### How to Avoid It

- Use friendly user-facing messages.
- Log detailed server-side errors with request IDs.
- Keep sensitive details out of the UI.
- Make retry behavior explicit.
- Preserve user input when submission fails.
- Add idempotency for payments, webhooks, and create actions.

## 14. Observability Missing Until Something Fails

### The Mistake

The app ships with no meaningful logs, metrics, alerts, or audit trail.

### Why It Happens

Monitoring does not improve the demo, so it is easy to skip.

### What Breaks

- You learn about downtime from users.
- Bugs cannot be reproduced.
- Slow queries and expensive endpoints go unnoticed.
- Abuse patterns are invisible.
- Customer support cannot answer what happened.

### How to Avoid It

- Add structured logs for important backend actions.
- Track error rate, latency, traffic, and resource usage.
- Alert on failed jobs, webhook failures, payment failures, and high error rates.
- Keep audit logs for admin and sensitive actions.
- Add a simple operational dashboard before launch.

## 15. Letting AI Agents Change Too Much at Once

### The Mistake

The builder asks the AI to "fix everything" or "make it production ready" in one large change.

### Why It Happens

AI tools reward broad prompts with broad-looking progress. Large diffs feel efficient until review becomes impossible.

### What Breaks

- Working features regress.
- Security changes are mixed with styling changes.
- Dead code and comments accumulate.
- The builder cannot tell which change caused a bug.
- The AI reintroduces old patterns in a different file.

### How to Avoid It

- Make small, reviewable changes.
- Ask for one concern at a time: auth, then validation, then error states, then tests.
- Read diffs before accepting them.
- Run tests after each meaningful change.
- Keep a changelog of architectural decisions.
- Delete stale comments and unused code.

## 16. Documentation Debt

### The Mistake

The app has code but no explanation of how to run, deploy, operate, or modify it.

### Why It Happens

AI can generate files faster than the builder can understand them.

### What Breaks

- New contributors cannot onboard.
- The builder forgets why choices were made.
- Environment setup becomes guesswork.
- Deployment depends on hidden local state.
- Support and incident response are improvised.

### How to Avoid It

- Keep a short `README` with setup, scripts, environment variables, and deployment notes.
- Maintain an architecture note for the data model and core flows.
- Document third-party services, webhooks, and scheduled jobs.
- Record manual operational tasks.
- Keep prompts or design notes only when they explain a durable decision.

## 17. Product Scope Creep

### The Mistake

Because features are easy to generate, the product grows before the core problem is validated.

### Why It Happens

AI reduces the friction of adding screens. It does not reduce the cost of maintaining them.

### What Breaks

- The app becomes broad but shallow.
- Users cannot tell what the product is for.
- More features create more permissions, states, tests, and support cases.
- The codebase becomes harder to secure and optimize.

### How to Avoid It

- Define the product's smallest valuable workflow.
- Finish the core loop before adding adjacent features.
- Remove generated features that do not serve the main user job.
- Track every feature's owner, data, permissions, and failure modes.

## Pre-Launch Checklist for Vibe-Coded Apps

### Product and UX

- The primary user and primary workflow are clear.
- The app has useful empty, loading, error, and success states.
- The main flow works on mobile and desktop.
- Users can recover from mistakes.
- Labels use user language, not internal implementation terms.
- Accessibility basics are checked: keyboard, focus, labels, contrast, semantics.

### Testing

- The idea has been tested with real or representative users.
- The main workflow has been tested without coaching the user.
- The top five critical flows are written down.
- Each critical flow has been tested for success, bad input, empty data, permission denial, slow network, and retry.
- Role-based access has been tested with separate accounts.
- Important APIs have been tested directly, not only through the UI.
- Mobile layouts have been tested on real viewport sizes.
- Accessibility checks cover keyboard navigation, focus, labels, contrast, and screen-reader basics.
- Realistic data has been used: long names, missing fields, duplicate values, large lists, time zones, and old records.
- Security checks include secrets, dependencies, authentication, authorization, uploads, CORS, and rate limits.
- Performance checks include page load, interaction delay, layout shift, query speed, and paid API usage.
- Staging smoke tests run before production.
- Production smoke tests run after deployment.
- Backup restore has been tested at least once.
- Known bugs and accepted risks are documented.

### Frontend

- No secrets are exposed in client bundles.
- Client-side checks are treated as convenience, not security.
- State has a clear source of truth.
- Forms preserve input on failure.
- Destructive actions have confirmation or undo.
- Bundle size and image size are measured.

### Backend

- Every API route checks authentication and authorization.
- Every object access checks ownership or tenant scope.
- Input is validated server-side.
- Important actions are idempotent.
- Errors are logged with request IDs.
- Rate limits exist for public, expensive, or abuse-prone endpoints.

### Database

- The data model reflects the real domain.
- Ownership and tenant boundaries are explicit.
- Important invariants have constraints.
- Migrations are tested before production.
- Backups are automated and restore-tested.
- Deletes are handled intentionally.

### Security

- Secrets live in environment variables or a secrets manager.
- Dependencies are reviewed and scanned.
- Auth/session settings are production-grade.
- CORS is restrictive.
- File uploads are validated and isolated.
- Logs do not contain sensitive data.
- Admin features are separately protected.

### Deployment

- Staging and production are separate.
- Production deploys are deliberate and reversible.
- Environment variables are documented.
- Health checks and smoke tests exist.
- Rollback steps are known.
- Hosting lock-in and export options are understood.

### Observability and Operations

- Errors, latency, traffic, and failed jobs are monitored.
- Alerts go somewhere a human checks.
- Audit logs exist for sensitive actions.
- Usage and spend alerts are set for paid services.
- Support has enough context to diagnose common failures.

### Performance and Cost

- Core Web Vitals are measured.
- Expensive API calls are cached or rate-limited.
- Lists are paginated.
- Database queries are indexed.
- Images are optimized.
- AI token usage is tracked.
- Hosting and third-party service limits are understood.

## Practical Workflow for Safer Vibe Coding

1. Prompt for a narrow feature.
2. Review the generated diff.
3. Ask the AI to explain the data flow and security assumptions.
4. Add or update tests.
5. Run formatters, linters, type checks, and tests.
6. Check dependency changes.
7. Test failure states manually.
8. Commit the small change.
9. Deploy to staging.
10. Promote to production only after smoke testing and backup confirmation.

## The Core Rule

Vibe coding is fast, but production is still production. If the app handles real users, money, private data, business workflows, or anything regulated, the minimum standard is not "the demo works." The minimum standard is: the system is understood, reviewed, tested, observable, recoverable, and secure enough for the risk it carries.
