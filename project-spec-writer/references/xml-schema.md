# Project Specification XML Schema Reference

This document defines each section of the `<project_specification>` XML structure. Use it as a checklist and structural guide when writing specs.

## Top-Level Structure

```xml
<project_specification>
  <project_name>...</project_name>
  <overview>...</overview>
  <scope_boundaries>...</scope_boundaries>
  <technology_stack>...</technology_stack>
  <prerequisites>...</prerequisites>
  <environment_variables>...</environment_variables>
  <file_structure>...</file_structure>
  <core_data_entities>...</core_data_entities>
  <authentication>...</authentication>
  <route_definitions>...</route_definitions>
  <component_hierarchy>...</component_hierarchy>
  <pages_and_interfaces>...</pages_and_interfaces>
  <core_functionality>...</core_functionality>
  <error_handling>...</error_handling>
  <third_party_integrations>...</third_party_integrations>
  <aesthetic_guidelines>...</aesthetic_guidelines>
  <security_considerations>...</security_considerations>
  <advanced_functionality>...</advanced_functionality>
  <final_integration_test>...</final_integration_test>
  <success_criteria>...</success_criteria>
  <build_output>...</build_output>
  <key_implementation_notes>...</key_implementation_notes>
</project_specification>
```

Not all sections are required for every project. Include only sections relevant to the project type.

---

## Section Details

### `<project_name>`
Single line. Format: `AppName - Short Description`.

### `<overview>`
3-4 paragraphs covering:
- What the app does (1st paragraph: core purpose and value proposition)
- Key features and user workflows (2nd paragraph)
- Critical architectural constraints (3rd paragraph, prefixed with `CRITICAL:` for hard rules like "no server", "offline-only", etc.)

### `<scope_boundaries>`
Explicitly define what is NOT part of this project. Prevents scope creep and sets clear expectations for the builder.

```xml
<scope_boundaries>
  <in_scope>
    - User authentication via email/password and Google OAuth
    - Task CRUD with drag-and-drop reordering
    - Real-time collaboration for up to 5 users per board
  </in_scope>
  <out_of_scope>
    - Native mobile apps (web-only, responsive)
    - Payment/billing features
    - Admin dashboard for user management
    - Email notification system
    - Data export/import beyond CSV
  </out_of_scope>
  <future_considerations>
    - Webhook integrations (Phase 2)
    - Custom fields on tasks (Phase 2)
    - Gantt chart view (Phase 3)
  </future_considerations>
</scope_boundaries>
```

Rules:
- `in_scope`: concrete features included in this build
- `out_of_scope`: things the builder should NOT implement, even if they seem implied
- `future_considerations`: features intentionally deferred, with rough phase labels

### `<technology_stack>`
Group by layer. Common sub-sections:

```xml
<technology_stack>
  <frontend_application>
    <framework>...</framework>
    <build_tool>...</build_tool>
    <styling>...</styling>
    <routing>...</routing>
    <state_management>...</state_management>
  </frontend_application>
  <data_layer>
    <database>...</database>
    <reactive_queries>...</reactive_queries>
    <search>...</search>
    <export>...</export>
    <note>...</note>  <!-- architectural constraints -->
  </data_layer>
  <backend> <!-- if applicable -->
    <runtime>...</runtime>
    <framework>...</framework>
    <auth>...</auth>
    <api_style>...</api_style>
  </backend>
  <build_output>
    <build_command>...</build_command>
    <note>...</note>
  </build_output>
  <libraries>
    <!-- one tag per library: name + version + purpose -->
    <dnd>@dnd-kit/core v6.3.1 for drag-and-drop</dnd>
    <charts>Recharts v3.5 for dashboard visualizations</charts>
  </libraries>
</technology_stack>
```

Rules:
- Always include exact version numbers
- State purpose after each library/tool
- Use `<note>` for architectural constraints ("NO server", "NO API", etc.)

### `<prerequisites>`
Sub-sections: `<environment_setup>` (runtime, tools) and `<build_configuration>` (build settings, plugins).

### `<environment_variables>`
List all environment variables the project requires. Prevents AI agents from hardcoding secrets or missing configuration.

```xml
<environment_variables>
  <variable>
    <name>DATABASE_URL</name>
    <description>PostgreSQL connection string</description>
    <required>true</required>
    <example>postgresql://user:pass@localhost:5432/mydb</example>
  </variable>
  <variable>
    <name>NEXT_PUBLIC_SUPABASE_URL</name>
    <description>Supabase project URL (public, safe for client)</description>
    <required>true</required>
    <example>https://xxx.supabase.co</example>
  </variable>
  <variable>
    <name>STRIPE_SECRET_KEY</name>
    <description>Stripe API secret key (server-only)</description>
    <required>false</required>
    <note>Only needed if payment features are enabled</note>
  </variable>
</environment_variables>
```

Rules:
- Mark each as required/optional
- Indicate client-safe vs server-only for frontend frameworks
- Provide realistic example values (never real secrets)
- Add `<note>` for conditional requirements

### `<file_structure>`
Exact folder/file tree for the project. AI agents can use this to scaffold the project immediately.

```xml
<file_structure>
src/
├── app/
│   ├── layout.tsx              # Root layout with providers
│   ├── page.tsx                # Landing/home page
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   └── signup/page.tsx
│   ├── dashboard/
│   │   ├── layout.tsx          # Dashboard shell with sidebar
│   │   ├── page.tsx            # Dashboard overview
│   │   └── projects/
│   │       ├── page.tsx        # Project list
│   │       └── [id]/page.tsx   # Single project view
│   └── api/
│       └── trpc/[trpc]/route.ts
├── components/
│   ├── ui/                     # Reusable primitives (Button, Input, Modal)
│   ├── layout/                 # Sidebar, Header, Footer
│   └── features/               # Feature-specific composites
│       ├── project/
│       └── task/
├── lib/
│   ├── supabase.ts             # Supabase client
│   ├── trpc.ts                 # tRPC client setup
│   └── utils.ts                # Shared utilities
├── server/
│   ├── routers/                # tRPC routers
│   └── db/                     # Database schema, migrations
├── types/                      # Shared TypeScript types
└── styles/
    └── globals.css             # Tailwind imports + custom CSS
</file_structure>
```

Rules:
- Use tree format with `├──` and `└──` connectors
- Add inline comments (`# description`) for non-obvious files
- Group by feature or layer depending on project convention
- Include config files at root (`.env.example`, `tailwind.config.ts`, etc.)

### `<core_data_entities>`
One child tag per entity. Each entity lists fields as `- field_name: type (constraints, description)`.

Field format examples:
```
- id: string (uuid)
- name: string (required, max 100 characters)
- status: enum (draft, active, archived)
- tags: string[] (array of tag IDs)
- settings: object (theme, notifications)
- createdAt: Date
- sortOrder: number (for manual ordering)
```

Include compound indexes when relevant to querying:
```
[projectId+status], [projectId+sprintId]
```

### `<authentication>`
Define the complete auth flow. Skip for projects with no user accounts.

```xml
<authentication>
  <strategy>Session-based with Supabase Auth</strategy>
  <providers>
    <email_password>
      - Sign up with email verification
      - Password reset via magic link
      - Minimum password: 8 chars, 1 uppercase, 1 number
    </email_password>
    <oauth>
      <google>Sign in with Google (default for quick onboarding)</google>
      <github>Sign in with GitHub (developer-focused audience)</github>
    </oauth>
  </providers>
  <session>
    <storage>HTTP-only cookie via Supabase SSR helper</storage>
    <duration>7 days, refresh on activity</duration>
    <refresh>Auto-refresh when token has less than 1 hour remaining</refresh>
  </session>
  <authorization>
    <roles>enum (owner, admin, member, viewer)</roles>
    <rules>
      - owner: full access, can delete project, transfer ownership
      - admin: manage members, edit settings, cannot delete project
      - member: create/edit own items, comment on others
      - viewer: read-only access to all project data
    </rules>
    <row_level_security>CRITICAL: All Supabase tables MUST have RLS policies. No direct table access without auth context.</row_level_security>
  </authorization>
  <protected_routes>
    - /dashboard/* — requires authenticated user
    - /admin/* — requires admin or owner role
    - /api/* — requires valid session token
  </protected_routes>
  <redirect_flows>
    - Unauthenticated user → /login (preserve intended destination)
    - After login → redirect to preserved destination or /dashboard
    - After signup → /onboarding (first-time flow)
  </redirect_flows>
</authentication>
```

### `<route_definitions>`
Complete URL structure. AI agents use this to scaffold all pages and set up routing guards.

```xml
<route_definitions>
  <public_routes>
    <route path="/" page="LandingPage" />
    <route path="/login" page="LoginPage" />
    <route path="/signup" page="SignupPage" />
    <route path="/reset-password" page="ResetPasswordPage" />
  </public_routes>
  <protected_routes guard="requireAuth">
    <route path="/dashboard" page="DashboardOverview" />
    <route path="/projects" page="ProjectListPage" />
    <route path="/projects/:id" page="ProjectDetailPage" />
    <route path="/projects/:id/settings" page="ProjectSettingsPage" guard="requireAdmin" />
    <route path="/settings" page="UserSettingsPage" />
  </protected_routes>
  <api_routes>
    <route path="/api/trpc/*" handler="tRPC router" />
    <route path="/api/webhooks/stripe" handler="Stripe webhook" method="POST" />
  </api_routes>
  <redirects>
    <redirect from="/app" to="/dashboard" status="301" />
  </redirects>
</route_definitions>
```

Rules:
- Use `:param` for dynamic segments
- Specify guards for protected routes (auth, role-based)
- Include API routes and webhooks
- List permanent redirects for legacy URLs

### `<component_hierarchy>`
Visual tree of React/UI components. Shows parent-child relationships and where shared components are reused.

```xml
<component_hierarchy>
  <app_shell>
    <providers> <!-- ThemeProvider → AuthProvider → QueryProvider → TRPCProvider -->
      <router>
        <!-- Public layout -->
        <public_layout>
          <navbar />                <!-- Logo, Login/Signup buttons -->
          <outlet />                <!-- LandingPage, LoginPage, etc. -->
          <footer />
        </public_layout>

        <!-- Authenticated layout -->
        <dashboard_layout>
          <sidebar>                 <!-- 240px fixed -->
            <workspace_switcher />
            <nav_links />           <!-- Dashboard, Projects, Settings -->
            <user_menu />           <!-- Avatar, logout -->
          </sidebar>
          <main_area>
            <top_bar>               <!-- Breadcrumb, search, notifications -->
              <breadcrumb />
              <global_search />
              <notification_bell />
            </top_bar>
            <page_content>          <!-- Scrollable area -->
              <outlet />            <!-- Dashboard, ProjectList, etc. -->
            </page_content>
          </main_area>
        </dashboard_layout>
      </router>
    </providers>
  </app_shell>

  <!-- Shared components (used across multiple pages) -->
  <shared>
    <modal />                       <!-- Generic modal wrapper -->
    <confirm_dialog />              <!-- Delete confirmation, etc. -->
    <toast_container />             <!-- Notification toasts -->
    <data_table />                  <!-- Sortable, filterable table -->
    <empty_state />                 <!-- Icon + message + CTA -->
    <loading_skeleton />            <!-- Placeholder while loading -->
  </shared>
</component_hierarchy>
```

Rules:
- Show nesting with indentation
- Add inline comments for dimensions, purpose
- Mark shared/reusable components separately
- Show provider wrapping order (outermost → innermost)

### `<pages_and_interfaces>`
The largest section. Organized hierarchically:

```xml
<pages_and_interfaces>
  <global_layout>
    <top_navigation>...</top_navigation>
    <sidebar>...</sidebar>
    <main_content>...</main_content>
  </global_layout>
  <page_name_view>
    <header>...</header>
    <main_section>...</main_section>
    <sub_component>...</sub_component>
    <empty_state>...</empty_state>
  </page_name_view>
  <!-- repeat for each page/view -->
  <keyboard_shortcuts_reference>...</keyboard_shortcuts_reference>
</pages_and_interfaces>
```

For each UI element, specify:
- Dimensions (px values: height, width, padding, gap)
- Colors (hex codes with semantic names)
- Behaviors (hover, click, drag, keyboard)
- Content structure (what appears, order, truncation)
- States (empty, loading, error, active, selected)
- Animations (duration, easing, effect)

### `<core_functionality>`
Group by functional domain. Each domain lists capabilities as bullet points.

```xml
<core_functionality>
  <entity_management>
    - CRUD operations
    - Relationships and linking
    - Bulk operations with specific actions listed
  </entity_management>
  <search_and_filter>...</search_and_filter>
  <data_persistence>...</data_persistence>
  <!-- etc. -->
</core_functionality>
```

### `<aesthetic_guidelines>`
The design system. Sub-sections:

```xml
<aesthetic_guidelines>
  <design_fusion>  <!-- high-level design philosophy -->
  <color_palette>
    <primary_colors>  <!-- brand colors with hex + usage -->
    <background_colors>
    <text_colors>
    <status_colors>
    <priority_colors>  <!-- or other semantic groups -->
    <dark_theme>  <!-- if applicable -->
  </color_palette>
  <typography>
    <font_families>  <!-- with fallback stacks -->
    <font_sizes>     <!-- with weight and context -->
    <line_heights>
  </typography>
  <spacing>  <!-- base unit and scale -->
  <borders_and_shadows>
    <borders>  <!-- thickness, color, radius -->
    <shadows>  <!-- named levels: card, dropdown, modal -->
  </borders_and_shadows>
  <component_styling>
    <!-- one sub-tag per component type: buttons, inputs, dropdowns, cards, badges, avatars, modals, panels -->
  </component_styling>
  <animations>
    <micro_interactions>
    <page_transitions>
    <drag_and_drop>
    <loading_states>
    <orchestrated_entrance>
  </animations>
  <responsive_design>
    <breakpoints>
      <!-- Define breakpoints with layout changes -->
    </breakpoints>
    <mobile_adaptations>
      <!-- How components transform on small screens -->
    </mobile_adaptations>
    <touch_interactions>
      <!-- Touch-specific behaviors (swipe, long-press) -->
    </touch_interactions>
  </responsive_design>
  <icons>  <!-- library, sizes, stroke -->
  <accessibility>  <!-- WCAG, focus, keyboard, motion -->
</aesthetic_guidelines>
```

#### Responsive Design Detail

The `<responsive_design>` section should specify:

```xml
<responsive_design>
  <breakpoints>
    - mobile: 0–639px (single column, bottom nav, full-width cards)
    - tablet: 640–1023px (collapsible sidebar, 2-column grid)
    - desktop: 1024–1279px (fixed sidebar, 3-column grid)
    - wide: 1280px+ (max-width 1440px container, centered)
  </breakpoints>
  <mobile_adaptations>
    - Sidebar → bottom tab bar (5 icons max, 56px height)
    - Data tables → card list view (one card per row)
    - Modal dialogs → full-screen sheets (slide up from bottom)
    - Multi-column layouts → single column, stacked
    - Hover tooltips → long-press tooltips (300ms delay)
    - Drag-and-drop → disabled on touch, use move up/down buttons
  </mobile_adaptations>
  <touch_interactions>
    - Swipe left on list item → reveal delete action (red, 80px)
    - Swipe right on list item → reveal archive action (blue, 80px)
    - Pull-to-refresh on list views (spinner appears at -60px threshold)
    - Long-press (500ms) on card → enter selection mode
    - Minimum tap target: 44x44px (WCAG 2.5.8)
  </touch_interactions>
</responsive_design>
```

Color format: `- Semantic Name: #HEX - usage description`

### `<error_handling>`
Define how the app communicates errors to users and how it recovers from failures.

```xml
<error_handling>
  <user_facing>
    <toast_notifications>
      - Success: green (#22C55E), 3s auto-dismiss, bottom-right
      - Error: red (#EF4444), persistent until dismissed, bottom-right
      - Warning: amber (#F59E0B), 5s auto-dismiss, bottom-right
      - Info: blue (#3B82F6), 3s auto-dismiss, bottom-right
      - Max 3 toasts stacked, oldest dismissed first
    </toast_notifications>
    <form_validation>
      - Inline errors below each field, red (#EF4444) text, 13px
      - Show on blur (not on keystroke) for better UX
      - Scroll to first error on submit
      - Shake animation (200ms) on invalid submit attempt
    </form_validation>
    <error_pages>
      - 404: illustration + "Page not found" + link to dashboard
      - 500: illustration + "Something went wrong" + retry button
      - 403: "You don't have access" + request access CTA
      - Offline: banner at top "You're offline. Changes will sync when reconnected."
    </error_pages>
  </user_facing>
  <error_boundaries>
    - Wrap each page in a React Error Boundary
    - Show fallback UI with "Something went wrong" + retry button
    - Log error details to console in development
  </error_boundaries>
  <api_errors>
    - Network failure: retry up to 3 times with exponential backoff (1s, 2s, 4s)
    - 401 Unauthorized: redirect to /login, clear session
    - 429 Rate limited: show "Too many requests, please wait" toast
    - 5xx: show generic error toast, log to error tracking
  </api_errors>
</error_handling>
```

### `<third_party_integrations>`
External services and APIs the project depends on. Include setup steps, SDK usage, and webhook handling.

```xml
<third_party_integrations>
  <integration name="Stripe">
    <purpose>Payment processing for subscription billing</purpose>
    <sdk>@stripe/stripe-js v2.4 (client) + stripe v14.x (server)</sdk>
    <features>
      - Checkout session for subscription signup
      - Customer portal for billing management
      - Webhook for payment events (invoice.paid, subscription.deleted)
    </features>
    <webhook_endpoint>/api/webhooks/stripe</webhook_endpoint>
    <events_handled>
      - checkout.session.completed → activate subscription
      - invoice.paid → extend billing period
      - customer.subscription.deleted → downgrade to free tier
    </events_handled>
  </integration>
  <integration name="Resend">
    <purpose>Transactional email (welcome, password reset, notifications)</purpose>
    <sdk>resend v3.x</sdk>
    <templates>
      - welcome_email: sent after signup confirmation
      - password_reset: magic link with 1h expiry
      - weekly_digest: project activity summary (opt-in)
    </templates>
  </integration>
</third_party_integrations>
```

### `<security_considerations>`
Security requirements and hardening measures. CRITICAL for any app handling user data.

```xml
<security_considerations>
  <input_validation>
    - CRITICAL: Sanitize ALL user input on the server side, even if validated on client
    - Use zod schemas for request validation on every API endpoint
    - Max input lengths: title (200 chars), description (10,000 chars), comment (5,000 chars)
    - Strip HTML tags from text inputs (use DOMPurify if rich text is needed)
  </input_validation>
  <authentication_security>
    - Passwords: bcrypt with cost factor 12 (handled by Supabase Auth)
    - Session tokens: HTTP-only, Secure, SameSite=Lax cookies
    - CSRF: Supabase Auth handles via cookie-based sessions
    - Rate limit login attempts: 5 per minute per IP
  </authentication_security>
  <data_protection>
    - CRITICAL: Never expose user IDs or internal IDs in URLs if predictable (use UUIDs)
    - Row Level Security on ALL Supabase tables
    - API responses must never include fields the requesting user shouldn't see
    - Soft-delete user data, hard-delete after 30 days
  </data_protection>
  <api_security>
    - All API routes require valid session (except public endpoints)
    - CORS: restrict to application domain only
    - Rate limiting: 100 requests/minute per authenticated user
    - File uploads: max 10MB, allowed types (image/png, image/jpeg, application/pdf)
  </api_security>
  <client_security>
    - CRITICAL: Never store secrets in client-side code or NEXT_PUBLIC_ env vars
    - Content Security Policy headers
    - Strict-Transport-Security header
    - X-Content-Type-Options: nosniff
  </client_security>
</security_considerations>
```

Rules:
- Prefix non-negotiable rules with `CRITICAL:`
- Be specific about limits (max lengths, rate limits, file sizes)
- Cover: input validation, auth, data protection, API, client-side, headers

### `<advanced_functionality>`
Features beyond core CRUD. Examples: bulk operations, keyboard shortcuts, smart defaults, notifications, offline support, multi-user.

### `<final_integration_test>`
Numbered test scenarios. Each scenario:

```xml
<test_scenario_N>
  <description>Scenario Title</description>
  <steps>
    1. Action step
    2. Verify expected result
    ...
  </steps>
</test_scenario_N>
```

Rules:
- 8-15 steps per scenario
- Alternate between user actions and verification steps
- Cover the critical user journeys end-to-end
- Include edge cases (empty states, limits, errors)

### `<success_criteria>`
Grouped by dimension:

```xml
<success_criteria>
  <functionality>  <!-- what must work -->
  <user_experience>  <!-- performance, usability -->
  <technical_quality>  <!-- code quality, architecture -->
  <visual_design>  <!-- design consistency -->
  <build>  <!-- deployment, compatibility -->
</success_criteria>
```

Each contains bullet points with specific, measurable criteria.

### `<build_output>`
Build command, output directory, contents description, deployment notes.

### `<key_implementation_notes>`
Technical guidance for the builder:

```xml
<key_implementation_notes>
  <critical_paths>  <!-- what to get right first -->
  <recommended_implementation_order>  <!-- numbered list -->
  <database_schema>  <!-- concrete code if applicable -->
  <performance_considerations>
  <testing_strategy>
  <tool_usage>  <!-- dev tools, screenshots, etc. -->
</key_implementation_notes>
```

---

## Section Applicability by Project Type

| Section | Web App | API/Backend | CLI Tool | Mobile | Library |
|---------|---------|-------------|----------|--------|---------|
| overview | ✅ | ✅ | ✅ | ✅ | ✅ |
| scope_boundaries | ✅ | ✅ | △ | ✅ | △ |
| technology_stack | ✅ | ✅ | ✅ | ✅ | ✅ |
| prerequisites | ✅ | ✅ | ✅ | ✅ | ✅ |
| environment_variables | ✅ | ✅ | △ | ✅ | ✗ |
| file_structure | ✅ | ✅ | ✅ | ✅ | ✅ |
| core_data_entities | ✅ | ✅ | △ | ✅ | △ |
| authentication | ✅ | ✅ | ✗ | ✅ | ✗ |
| route_definitions | ✅ | ✅ | ✗ | ✅ | ✗ |
| component_hierarchy | ✅ | ✗ | ✗ | ✅ | ✗ |
| pages_and_interfaces | ✅ | ✗ | △ | ✅ | ✗ |
| core_functionality | ✅ | ✅ | ✅ | ✅ | ✅ |
| error_handling | ✅ | ✅ | ✅ | ✅ | △ |
| third_party_integrations | ✅ | ✅ | △ | ✅ | △ |
| aesthetic_guidelines | ✅ | ✗ | ✗ | ✅ | ✗ |
| security_considerations | ✅ | ✅ | △ | ✅ | △ |
| advanced_functionality | ✅ | △ | △ | ✅ | △ |
| final_integration_test | ✅ | ✅ | ✅ | ✅ | ✅ |
| success_criteria | ✅ | ✅ | ✅ | ✅ | ✅ |
| build_output | ✅ | ✅ | ✅ | ✅ | ✅ |
| key_implementation_notes | ✅ | ✅ | ✅ | ✅ | ✅ |

✅ = Include, △ = Optional, ✗ = Skip

---

## Writing Quality Checklist

- [ ] Every color is a hex code, not a name
- [ ] Every dimension is in px (or rem/% with rationale)
- [ ] Every library has an exact version number
- [ ] Every enum lists all possible values
- [ ] Data entities have complete field definitions with types
- [ ] UI specs include hover, active, disabled, empty states
- [ ] Keyboard shortcuts are specified for all key interactions
- [ ] Animations specify duration and easing
- [ ] Success criteria are measurable (numbers, not vague qualities)
- [ ] Implementation order reflects dependency chain
- [ ] Test scenarios cover all critical user journeys
- [ ] Scope boundaries clearly state what is out of scope
- [ ] File structure tree covers all major directories and key files
- [ ] Component hierarchy shows provider wrapping order and shared components
- [ ] Responsive breakpoints defined with mobile layout adaptations
- [ ] Auth flow covers login, signup, session, roles, and protected routes
- [ ] Error handling covers toasts, form validation, error pages, and API errors
- [ ] Security section addresses input validation, data protection, and API security
- [ ] All environment variables listed with required/optional and example values
- [ ] Route definitions cover all pages, guards, and API endpoints
- [ ] Third-party integrations list SDKs, webhooks, and event handlers
