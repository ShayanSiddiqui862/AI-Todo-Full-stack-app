name: frontend-master
description: Expert Next.js 16+ App Router and Better Auth orchestration for full-stack SDD. Use when creating components, pages, or auth flows.
dependencies: next@>=16.0.0, better-auth@latest, tailwindcss@>=4.0.0


# Frontend Master Skill

This skill provides advanced instructions for building professional-grade UIs using the Next.js 16 App Router. It ensures strict compliance with the Phase II monorepo architecture and authentication security models.

## Core Workflow (SDD Lifecycle)
1. **Spec Alignment**: Before modifying code, search for and read the target specification (e.g., `@specs/ui/components.md`).
2. **Task Verification**: Ensure a valid Task ID from `speckit.tasks` exists. If not, stop and request the task breakdown.
3. **Draft Implementation**: Propose small, testable diffs.
4. **Linkage**: Add a comment at the top of new files: `// Task-ID: [T-XXX] | Spec: [path/to/spec]`.

## Next.js 16 Best Practices
- **Turbopack Usage**: Always optimize for the default Turbopack bundler for faster development.
- **Async Metadata**: Always handle `params` and `searchParams` asynchronously in layouts and pages.
- **Partial Prerendering (PPR)**: Leverage PPR for pages with dynamic content shells to improve perceived performance.
- **Proxy Pattern**: Use `proxy.ts` (formerly middleware) for network boundary control and request interception.

## Better Auth Integration Patterns
- **Client Handshake**: Use `createAuthClient` from `better-auth/react` to manage frontend sessions.
- **JWT Middleware**: Ensure the `Authorization: Bearer <token>` header is automatically attached by the central API client in `/lib/api.ts`.
- **Server-Side Validation**: Use `auth.api.getSession()` in Server Components to prevent layout shifts during authentication checks.

## Quality Standards
- **Zero Inline Styles**: Strictly use Tailwind CSS for all layouts and components.
- **RSC by Default**: Use Server Components for all data fetching; apply `'use client'` only for interactive logic (hooks, event listeners).
- **Error Boundaries**: Wrap major routes in `error.tsx` and provide lightweight `loading.tsx` fallbacks.

## Examples
### Safe API Fetching (Client Component)
```typescript
'use client';
import { useAuth } from '@/hooks/useAuth';
import { api } from '@/lib/api';

export const TaskList = () => {
  const { userId, token } = useAuth();
  // Skill: Automatically injects JWT Bearer token via api client
  const { data: tasks } = useSWR(`/api/${userId}/tasks`, () => api.getTasks(token));
  return <div>{/* Render tasks */}</div>;
};