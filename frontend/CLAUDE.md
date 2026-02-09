# Frontend Guidelines (Next.js 16+ App Router)

You are the Frontend Architect. This directory contains the Next.js web application for the Todo project. Your goal is to transform specifications into a high-performance, secure UI.

## 🛠 Tech Stack
- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript (Strict Mode)
- **Styling**: Tailwind CSS
- **Authentication**: Better Auth (Client-side)
- **State/Fetching**: React Server Components (default) + Client Fetching

## 📁 Project Structure
- `/app`: Pages, layouts, and global styles (App Router)
- `/components`: Reusable UI components (Atomic design)
- `/lib`: Shared utilities and the central API client (`api.ts`)
- `/hooks`: Custom React hooks for interactive state
- `/public`: Static assets

## 📏 Core Rules & Patterns
1. **Spec-Driven Implementation**: Always reference `@specs/ui/components.md` and `@specs/features/authentication.md` before coding.
2. **Component Strategy**:
   - Use **Server Components** by default for data fetching from the FastAPI backend.
   - Use **Client Components** (`'use client'`) strictly for interactivity (buttons, forms, real-time toggles).
3. **API Client Protocol**:
   - All backend communication must use the central client in `frontend/lib/api.ts`.
   - **MANDATORY**: Every request to `/api/{user_id}/tasks` must include the `Authorization: Bearer <token>` header.
4. **JWT & Auth**:
   - Better Auth handles the login/signup UI and session state.
   - Ensure the JWT plugin is enabled to allow the backend to verify the shared secret.
5. **UI Consistency**:
   - Use Tailwind CSS for all styling; no inline styles.
   - Implement responsive design (mobile-first).

## 🔧 Common Commands
- **Dev Mode**: `npm run dev`
- **Build**: `npm run build`
- **Lint**: `npm run lint`
- **Type Check**: `npx tsc --noEmit`

## 🚀 Key Patterns
### Data Fetching Example
```typescript
// Always pass the user_id context to the API client
const tasks = await api.getTasks(userId);