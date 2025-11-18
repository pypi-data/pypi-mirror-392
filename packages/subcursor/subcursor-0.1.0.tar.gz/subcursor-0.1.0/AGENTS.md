# subcursor: Guide for AI Agents

**Target Audience**: AI Assistants (Claude, GPT, etc.) using Cursor with subcursor installed

This document helps you (an AI agent) understand and effectively use subcursor's subagent system.

## What is subcursor?

subcursor allows spawning specialized instances of Cursor (subagents), each with different rules and capabilities. Think of it as calling in expert colleagues:

- **Designer subagent**: Focuses on UI/UX, visual design, CSS, accessibility
- **Backend subagent**: Specializes in APIs, databases, server architecture
- **Frontend subagent**: Experts in React, TypeScript, modern web frameworks
- **Custom subagents**: Domain-specific experts you can create

## When to Use Subagents

### Good Use Cases

✅ **Specialized Tasks Outside Your Current Focus**
```
User: "I need a beautiful landing page hero section"
You: → spawn designer subagent (UI/UX specialist handles it)
```

✅ **Domain Expertise You Lack**
```
User: "Set up a PostgreSQL connection pool with proper error handling"
You (frontend expert): → spawn backend subagent
```

✅ **Parallel Workstreams**
```
User: "Build user auth API and the login form"
You: → spawn backend for API, spawn frontend for form
```

✅ **Complex Multi-Domain Projects**
```
User: "Create a full e-commerce checkout flow"
You: → Orchestrate designer (UI), backend (payments), frontend (React)
```

### When NOT to Use

❌ **Simple tasks within your expertise**
❌ **Questions/explanations (no code needed)**
❌ **When context sharing is critical** (subagents don't see each other's work)
❌ **Quick iterations on current work**

## Available MCP Tools

subcursor provides three MCP tools:

### 1. list-subagents

**Purpose**: See available subagents and their capabilities

**When to use**:
- User asks what specialists are available
- You need to choose the right subagent
- Exploring customization options

**Example**:
```
User: "What kind of help can I get?"
You: Call list-subagents tool → show user the available specialists
```

### 2. spawn-subagent

**Purpose**: Launch a specialized Cursor instance

**Parameters**:
- `name` (required): Subagent name (e.g., "designer", "backend", "frontend")
- `prompt` (required): Specific task for the subagent
- `workspace_path` (optional): Custom workspace (defaults to current project)

**When to use**:
- Task clearly needs specialized expertise
- User explicitly requests a specific type of work
- You're not the best agent for the job

**Example**:
```
User: "I need a REST API for user authentication"
You: spawn-subagent
     name: "backend"
     prompt: "Create a REST API with JWT authentication, user registration,
              login, and password reset endpoints using best security practices"
```

**Good Prompts for Subagents**:
- ✅ Specific: "Create a modal component with backdrop, close button, and keyboard support"
- ✅ Context-rich: "Build API endpoints for /users with CRUD operations, validation, and error handling"
- ✅ Goal-oriented: "Design a dashboard layout with sidebar navigation and responsive grid"

**Poor Prompts**:
- ❌ Vague: "Help with the frontend"
- ❌ Too broad: "Build the app"
- ❌ No context: "Fix this"

### 3. create-subagent

**Purpose**: Define a new specialist for custom domains

**Parameters**:
- `name` (required): Subagent identifier (e.g., "ml-engineer", "devops")
- `description` (required): Clear description of their expertise

**When to use**:
- User has recurring needs in a specific domain
- Existing subagents don't cover the use case
- Building a specialized development workflow

**Example**:
```
User: "We do a lot of machine learning work"
You: create-subagent
     name: "ml-engineer"
     description: "Machine learning specialist: model training, data pipelines,
                   PyTorch/TensorFlow, feature engineering, MLOps"
```

## Decision Tree: Which Subagent?

```
Task involves UI/design/CSS/visual appeal?
  → designer

Task involves server/API/database/auth?
  → backend

Task involves React/Next/frontend framework?
  → frontend

Task involves DevOps/CI/deployment?
  → Create or use devops subagent

Task involves ML/data science?
  → Create or use ml-engineer subagent

Task is general or unclear?
  → Ask user for clarification OR handle it yourself
```

## Communication Patterns

### Pattern 1: Direct Handoff

```
You: "This task needs specialized UI/UX expertise. I'll spawn our designer subagent."
[spawn designer with detailed prompt]
You: "I've launched a designer subagent in a new window to handle the UI work."
```

### Pattern 2: Parallel Delegation

```
You: "I'll coordinate this multi-part task:"
You: "1. Spawning backend subagent for API development"
[spawn backend]
You: "2. Spawning frontend subagent for UI components"
[spawn frontend]
You: "Both specialists are now working in separate windows."
```

### Pattern 3: Creating Specialists

```
You: "I notice you frequently need security auditing. Let me create a specialist:"
[create security-auditor subagent]
You: "Created a security specialist. I'll spawn them for this task:"
[spawn security-auditor]
```

## Best Practices for AI Agents

### DO:

✅ **Give context-rich prompts** to subagents
```
Good: "Create a user profile page with avatar upload, edit form (name, email, bio),
       form validation, loading states, and error handling. Use React with TypeScript."
```

✅ **Explain to the user** what you're doing
```
"I'm spawning a backend specialist to handle the database architecture
 since that requires deep expertise in PostgreSQL optimization."
```

✅ **Choose the right specialist** for the task
```
UI mockup needed? → designer
API endpoint? → backend
React component? → frontend
```

✅ **Create custom subagents** for recurring needs
```
User does lots of Rust? → Create rust-systems-programmer
User has specific security requirements? → Create security-auditor
```

### DON'T:

❌ **Over-delegate simple tasks**
```
Bad: Spawning subagent for "add a console.log"
```

❌ **Spawn without explanation**
```
Bad: [silently spawn subagent]
Good: "This needs design expertise, spawning designer subagent to create the icon"
```

❌ **Use vague prompts**
```
Bad: spawn-subagent("designer", "help with UI")
Good: spawn-subagent("designer", "Create a navigation bar with logo, menu items,
                      search input, and user avatar. Mobile-responsive with hamburger menu.")
```

❌ **Expect subagents to collaborate automatically**
```
Subagents work independently - you need to coordinate between them
```

## Understanding Subagent Capabilities

Each subagent has custom `.cursorrules` that define their:

1. **Role**: What they specialize in
2. **Expertise**: Technologies and techniques they know
3. **Guidelines**: How they approach problems
4. **Communication style**: How they interact

### Designer Subagent
- **Strong at**: Visual design, CSS, UI/UX, accessibility, design systems
- **Uses**: Tailwind, modern CSS, SVG, semantic HTML
- **Focuses on**: User experience, aesthetics, responsive design

### Backend Subagent
- **Strong at**: API design, database schemas, authentication, security
- **Uses**: FastAPI, Express, PostgreSQL, Redis, microservices
- **Focuses on**: Scalability, security, proper architecture

### Frontend Subagent
- **Strong at**: React patterns, TypeScript, state management, performance
- **Uses**: React 18+, Next.js, TypeScript, modern build tools
- **Focuses on**: Component architecture, type safety, optimization

## Advanced Usage

### Orchestrating Multiple Subagents

```
User: "Build a real-time chat application"

You (coordinator):
1. Analyze requirements → identify domains
2. spawn backend: "WebSocket server, message persistence, auth"
3. spawn frontend: "Chat UI with real-time messages, user list, input"
4. spawn designer: "Chat bubble design, color scheme, avatars"

Then guide user to integrate the work from each subagent.
```

### Creating Specialized Workflows

```
User: "We follow strict security practices"

You:
1. create-subagent("security-auditor", "Security specialist...")
2. For future tasks: Always spawn security-auditor for reviews
3. Document the workflow for the user
```

### When You're Already a Subagent

If you're currently running as a subagent (check your own rules):
- Stay focused on your specialty
- Don't spawn other subagents (coordinate through the main agent)
- Be explicit about your domain boundaries

## Example Scenarios

### Scenario 1: User Needs Icon Design

```
User: "Create a logo for my app"
You: [recognize this is design work]
     spawn-subagent(
       name: "designer",
       prompt: "Create a modern app logo for [user's app description].
                Provide SVG format with multiple size variations."
     )
     "I've launched our designer specialist to create your logo."
```

### Scenario 2: Complex Full-Stack Feature

```
User: "Add social login to the app"
You: [analyze: needs backend OAuth + frontend buttons]
     spawn-subagent(
       name: "backend",
       prompt: "Implement OAuth 2.0 social login for Google and GitHub.
                Include user creation/linking, token management, and security."
     )
     spawn-subagent(
       name: "frontend",
       prompt: "Create social login buttons for Google and GitHub with proper
                branding, loading states, and error handling."
     )
     "I've started backend and frontend specialists to implement social login."
```

### Scenario 3: User Needs Custom Expertise

```
User: "I work extensively with embedded systems"
You: [no matching subagent]
     create-subagent(
       name: "embedded-systems",
       description: "Embedded systems specialist: C/C++, ARM, RTOS, hardware
                     interfaces, memory optimization, real-time constraints"
     )
     "Created an embedded systems specialist for your needs."
     [then spawn it for their current task]
```

## Troubleshooting

If subagents aren't available:
1. Check MCP server is configured (user should have done this)
2. Suggest user restart Cursor
3. Point them to USAGE.md for setup help

If wrong subagent was spawned:
- Spawn the correct one with a better prompt
- Each runs independently

## Summary

**subcursor's Purpose**: Give you the ability to delegate specialized work to focused AI instances

**Your Role**: Intelligent coordinator who:
- Recognizes when specialized expertise is needed
- Chooses the right specialist
- Provides clear, detailed prompts
- Explains the orchestration to the user

**Key Insight**: You're not just an AI assistant, you're a **tech lead** coordinating a team of specialists.

Use subcursor when it makes sense. Don't use it when you can handle the task well yourself. The goal is better outcomes through appropriate expertise, not more complexity.

