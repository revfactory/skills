# Example Spec: TaskFlow (Simple Project)

This is a reference example showing how a completed spec looks for a simple "Medium" complexity project. Use this as a structural guide when writing specs.

---

```xml
<project_specification>

<project_name>TaskFlow - Personal Task Management App</project_name>

<overview>
TaskFlow is a personal task management web application that helps individual users organize their daily work with projects, tasks, and due dates. It features a clean, minimal interface inspired by Things 3 and Todoist.

Key features include: project-based task organization, due date tracking with calendar view, drag-and-drop task reordering, keyboard-first navigation, and a "Today" smart view that surfaces tasks due today or overdue.

CRITICAL: This is a local-first application. All data is stored in the browser using IndexedDB via Dexie.js. There is NO backend server, NO user accounts, and NO network requests. The app must work fully offline after initial load.
</overview>

<scope_boundaries>
  <in_scope>
    - Project CRUD (create, rename, reorder, delete with all tasks)
    - Task CRUD with title, notes, due date, priority, project assignment
    - Drag-and-drop reordering within and across projects
    - "Today" view: tasks due today or overdue
    - "Upcoming" view: tasks grouped by date for next 14 days
    - Calendar date picker for due dates
    - Keyboard shortcuts for all major actions
    - Data persistence via IndexedDB
    - Light/dark theme toggle
  </in_scope>
  <out_of_scope>
    - User accounts, login, or authentication
    - Cloud sync or multi-device support
    - Collaboration or sharing features
    - Recurring tasks
    - File attachments
    - Mobile native apps (responsive web only)
    - Notifications or reminders
  </out_of_scope>
  <future_considerations>
    - JSON export/import for backup
    - Recurring tasks
    - Tags and filters
  </future_considerations>
</scope_boundaries>

<technology_stack>
  <frontend_application>
    <framework>React 19 with TypeScript 5.7</framework>
    <build_tool>Vite 6.1</build_tool>
    <styling>Tailwind CSS v4.0</styling>
    <routing>React Router v7.2 (hash-based routing for static hosting)</routing>
    <state_management>Zustand v5.0 for UI state, Dexie.js liveQuery for data</state_management>
  </frontend_application>
  <data_layer>
    <database>IndexedDB via Dexie.js v4.0</database>
    <reactive_queries>dexie-react-hooks for live-updating queries</reactive_queries>
    <note>CRITICAL: NO backend. NO fetch/axios. ALL data in IndexedDB only.</note>
  </data_layer>
  <libraries>
    <dnd>@dnd-kit/core v6.3 + @dnd-kit/sortable v9.0 for drag-and-drop</dnd>
    <icons>Lucide React v0.468 for icons</icons>
    <dates>date-fns v4.1 for date formatting and calculations</dates>
    <ids>nanoid v5.1 for generating unique IDs</ids>
  </libraries>
</technology_stack>

<prerequisites>
  <environment_setup>
    - Node.js v20+ and npm v10+
    - Modern browser with IndexedDB support (Chrome 80+, Firefox 78+, Safari 14+)
  </environment_setup>
  <build_configuration>
    - Vite with React plugin
    - TypeScript strict mode enabled
    - Tailwind CSS v4 with @tailwindcss/vite plugin
    - Path alias: @ → src/
  </build_configuration>
</prerequisites>

<environment_variables>
  <!-- No environment variables needed — this is a fully client-side app -->
  <note>No .env file required. No API keys, no server URLs. All configuration is compile-time via vite.config.ts.</note>
</environment_variables>

<file_structure>
src/
├── app.tsx                     # Root component with router
├── main.tsx                    # Entry point, renders App
├── db/
│   ├── index.ts                # Dexie database instance + schema
│   └── seed.ts                 # Optional: seed data for development
├── components/
│   ├── ui/                     # Reusable primitives
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── modal.tsx
│   │   ├── dropdown-menu.tsx
│   │   ├── date-picker.tsx
│   │   └── empty-state.tsx
│   ├── layout/
│   │   ├── sidebar.tsx         # Project list + smart views
│   │   ├── main-panel.tsx      # Right content area
│   │   └── app-shell.tsx       # Sidebar + main layout
│   └── features/
│       ├── task-item.tsx        # Single task row (checkbox, title, due date)
│       ├── task-list.tsx        # Sortable list of tasks
│       ├── task-detail.tsx      # Task edit panel (title, notes, date, priority)
│       ├── project-item.tsx     # Sidebar project entry
│       └── inline-add-task.tsx  # Quick-add task input
├── views/
│   ├── today-view.tsx           # Tasks due today/overdue
│   ├── upcoming-view.tsx        # Next 14 days grouped by date
│   ├── project-view.tsx         # Single project's tasks
│   └── all-tasks-view.tsx       # Every task, grouped by project
├── stores/
│   └── ui-store.ts              # Zustand: selected task, sidebar state, theme
├── hooks/
│   ├── use-tasks.ts             # Dexie liveQuery wrappers for tasks
│   ├── use-projects.ts          # Dexie liveQuery wrappers for projects
│   └── use-keyboard-shortcuts.ts
├── lib/
│   ├── utils.ts                 # cn() helper, date helpers
│   └── constants.ts             # Priority labels, colors, keyboard mappings
├── types/
│   └── index.ts                 # Task, Project, Priority types
└── styles/
    └── globals.css              # Tailwind imports, custom scrollbar styles
</file_structure>

<core_data_entities>
  <project>
    - id: string (nanoid, 21 chars)
    - name: string (required, max 100 chars)
    - color: string (hex code, default #3B82F6)
    - sortOrder: number (for manual ordering in sidebar)
    - createdAt: Date
    - updatedAt: Date
    Indexes: [sortOrder]
  </project>

  <task>
    - id: string (nanoid, 21 chars)
    - title: string (required, max 500 chars)
    - notes: string (optional, max 5000 chars, plain text)
    - completed: boolean (default false)
    - completedAt: Date | null
    - dueDate: Date | null
    - priority: enum (none, low, medium, high) — default: none
    - projectId: string | null (FK to project.id, null = Inbox)
    - sortOrder: number (within project, for manual reordering)
    - createdAt: Date
    - updatedAt: Date
    Indexes: [projectId+sortOrder], [dueDate], [completed]
  </task>
</core_data_entities>

<route_definitions>
  <routes>
    <route path="/" redirect="/today" />
    <route path="/today" page="TodayView" />
    <route path="/upcoming" page="UpcomingView" />
    <route path="/all" page="AllTasksView" />
    <route path="/project/:id" page="ProjectView" />
  </routes>
  <note>Hash-based routing (#/today) for static file hosting compatibility.</note>
</route_definitions>

<component_hierarchy>
  <app>
    <theme_provider>  <!-- Light/dark mode context -->
      <router>
        <app_shell>
          <sidebar width="260px">
            <app_logo />            <!-- "TaskFlow" text logo -->
            <smart_views>           <!-- Today, Upcoming, All -->
              <nav_item />
            </smart_views>
            <divider />
            <project_list>          <!-- Sortable project list -->
              <project_item />      <!-- Color dot + name + task count -->
              <add_project_button />
            </project_list>
            <sidebar_footer>        <!-- Theme toggle, keyboard help -->
              <theme_toggle />
            </sidebar_footer>
          </sidebar>
          <main_panel>
            <view_header />         <!-- View title + task count -->
            <task_list>             <!-- Sortable via dnd-kit -->
              <task_item />         <!-- Checkbox + title + due badge + priority dot -->
            </task_list>
            <inline_add_task />     <!-- Quick add at bottom -->
          </main_panel>
          <task_detail_panel>       <!-- Slides in from right, 360px -->
            <title_input />
            <notes_textarea />
            <date_picker />
            <priority_selector />
            <project_selector />
            <delete_button />
          </task_detail_panel>
        </app_shell>
      </router>
    </theme_provider>
  </app>

  <shared>
    <modal />
    <confirm_dialog />
    <dropdown_menu />
    <date_picker />
    <empty_state />
  </shared>
</component_hierarchy>

<pages_and_interfaces>
  <global_layout>
    <sidebar>
      - Fixed left panel, 260px width, full height
      - Background: #FAFAFA (light) / #1A1A1A (dark)
      - Border-right: 1px solid #E5E7EB (light) / #2D2D2D (dark)
      - Smart views section: Today (sun icon), Upcoming (calendar icon), All Tasks (inbox icon)
      - Each nav item: 36px height, 12px horizontal padding, 6px gap between icon and label
      - Active state: background #EFF6FF (light) / #1E3A5F (dark), text #2563EB
      - Badge on right: task count, 20px circle, #E5E7EB bg, 12px font
      - Projects section: header "Projects" in 11px uppercase #9CA3AF, 16px bottom margin
      - Each project: color dot (8px circle) + name + count badge
      - "Add Project" button: dashed border, #9CA3AF text, full width
    </sidebar>

    <main_panel>
      - Flex-grow, min-width 400px
      - Padding: 32px horizontal, 24px top
      - Max content width: 720px, centered
    </main_panel>
  </global_layout>

  <today_view>
    <header>
      - Title: "Today" in 28px / 700 weight
      - Subtitle: formatted date "Wednesday, February 19" in 14px #6B7280
      - Task count badge: "5 tasks" in 13px #9CA3AF
    </header>
    <overdue_section>
      - Appears only if overdue tasks exist
      - Header: "Overdue" in 13px uppercase #EF4444, with count
      - Tasks sorted by due date ascending (oldest first)
    </overdue_section>
    <today_section>
      - Header: "Today" in 13px uppercase #6B7280
      - Tasks sorted by priority (high → none), then sortOrder
    </today_section>
    <empty_state>
      - Icon: checkmark circle (48px, #22C55E)
      - Title: "All caught up!" in 18px / 600 weight
      - Subtitle: "No tasks due today." in 14px #9CA3AF
    </empty_state>
  </today_view>

  <task_item>
    - Height: 44px, padding 8px 12px
    - Checkbox: 18px circle, border 2px #D1D5DB, hover border #9CA3AF
    - Completed checkbox: filled #22C55E, white checkmark
    - Title: 15px, #111827 (light) / #F9FAFB (dark), truncate with ellipsis
    - Completed title: line-through, #9CA3AF
    - Due badge (right): "Today" #2563EB, "Tomorrow" #6B7280, "Overdue" #EF4444, future dates in #6B7280
    - Priority dot: 6px circle, left of title. High: #EF4444, Medium: #F59E0B, Low: #3B82F6, None: hidden
    - Hover: background #F9FAFB (light) / #262626 (dark)
    - Click: select task, open detail panel
    - Drag handle: 6-dot grip icon, visible on hover, left edge
    - Complete animation: checkbox fills green, title fades + strikethrough, row slides out after 800ms delay
  </task_item>

  <task_detail_panel>
    - Width: 360px, slides in from right with 200ms ease-out
    - Background: #FFFFFF (light) / #1F1F1F (dark)
    - Border-left: 1px solid #E5E7EB (light) / #2D2D2D (dark)
    - Close button: X icon, top-right, 32px
    - Title input: 20px / 600 weight, no visible border, full width
    - Notes textarea: 14px, auto-resize height, placeholder "Add notes..."
    - Due date: calendar icon + date picker dropdown
    - Priority: 4 radio buttons (None, Low, Medium, High) with color dots
    - Project: dropdown selector with color dots
    - Delete: red text button at bottom, requires confirmation dialog
    - Auto-save: debounce 500ms after each field change
  </task_detail_panel>

  <keyboard_shortcuts_reference>
    - n: New task (focus inline add input)
    - Enter: Save task and create next
    - Escape: Close detail panel / cancel edit
    - ↑/↓: Navigate task list
    - Space: Toggle selected task completion
    - Cmd+Delete: Delete selected task (with confirmation)
    - 1/2/3/4: Set priority (None/Low/Medium/High)
    - t: Set due date to today
    - Cmd+1: Go to Today view
    - Cmd+2: Go to Upcoming view
    - Cmd+3: Go to All Tasks view
  </keyboard_shortcuts_reference>
</pages_and_interfaces>

<core_functionality>
  <task_management>
    - Create task: inline input at bottom of list, Enter to save
    - Edit task: click to open detail panel, auto-save on change
    - Complete task: click checkbox, 800ms delay then hide (undo available during delay)
    - Delete task: from detail panel, confirmation required
    - Reorder tasks: drag-and-drop within list, updates sortOrder
    - Move task to project: dropdown in detail panel or drag to sidebar project
  </task_management>

  <project_management>
    - Create project: "Add Project" button, inline name input
    - Rename project: double-click name in sidebar
    - Delete project: right-click context menu, moves tasks to Inbox or deletes all (user choice)
    - Reorder projects: drag-and-drop in sidebar
    - Project colors: 8 preset color options in dropdown
  </project_management>

  <smart_views>
    - Today: tasks where dueDate = today OR dueDate < today (overdue), not completed
    - Upcoming: tasks with dueDate in next 14 days, grouped by date, not completed
    - All Tasks: all incomplete tasks grouped by project (Inbox first)
  </smart_views>

  <data_persistence>
    - All changes saved to IndexedDB immediately (via Dexie)
    - Live queries auto-update UI when data changes
    - No manual save button needed
  </data_persistence>
</core_functionality>

<error_handling>
  <user_facing>
    <form_validation>
      - Task title required: red border on empty submit, "Title is required" below
      - Project name required: same pattern
      - Max length enforcement: counter shows "450/500" when approaching limit
    </form_validation>
    <error_states>
      - IndexedDB unavailable (private browsing): full-page message explaining the limitation
      - Storage quota exceeded: toast warning "Storage is almost full. Consider deleting old completed tasks."
    </error_states>
  </user_facing>
  <note>No network errors to handle — this is a fully offline app.</note>
</error_handling>

<aesthetic_guidelines>
  <design_philosophy>
    Minimal, content-focused design inspired by Things 3. Generous whitespace, subtle borders, no heavy shadows. The interface should feel calm and organized.
  </design_philosophy>

  <color_palette>
    <light_theme>
      - Background: #FFFFFF
      - Sidebar bg: #FAFAFA
      - Surface: #F9FAFB
      - Border: #E5E7EB
      - Text primary: #111827
      - Text secondary: #6B7280
      - Text muted: #9CA3AF
      - Accent: #2563EB
      - Success: #22C55E
      - Warning: #F59E0B
      - Danger: #EF4444
    </light_theme>
    <dark_theme>
      - Background: #0F0F0F
      - Sidebar bg: #1A1A1A
      - Surface: #262626
      - Border: #2D2D2D
      - Text primary: #F9FAFB
      - Text secondary: #9CA3AF
      - Text muted: #6B7280
      - Accent: #60A5FA
      - Success: #4ADE80
      - Warning: #FBBF24
      - Danger: #F87171
    </dark_theme>
    <priority_colors>
      - High: #EF4444
      - Medium: #F59E0B
      - Low: #3B82F6
      - None: transparent
    </priority_colors>
  </color_palette>

  <typography>
    <font_families>
      - Primary: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif
      - Monospace: "JetBrains Mono", "Fira Code", monospace (for keyboard shortcut hints)
    </font_families>
    <font_sizes>
      - View title: 28px / 700
      - Section header: 13px / 600 uppercase tracking-wide
      - Task title: 15px / 400
      - Body/notes: 14px / 400
      - Caption/badge: 12px / 500
      - Sidebar nav: 14px / 500
    </font_sizes>
  </typography>

  <spacing>
    - Base unit: 4px
    - Scale: 4, 8, 12, 16, 20, 24, 32, 48, 64
  </spacing>

  <responsive_design>
    <breakpoints>
      - mobile: 0–767px (sidebar hidden, hamburger menu, full-width task list)
      - tablet: 768–1023px (collapsible sidebar overlay, no detail panel — use modal)
      - desktop: 1024px+ (full layout: sidebar + main + detail panel)
    </breakpoints>
    <mobile_adaptations>
      - Sidebar → slide-in drawer from left (280px, overlay with backdrop)
      - Task detail panel → full-screen modal (slide up)
      - Drag-and-drop → disabled, use move up/down buttons instead
      - Keyboard shortcuts → disabled on mobile
      - Minimum tap target: 44x44px
    </mobile_adaptations>
  </responsive_design>

  <animations>
    - Task complete: checkbox fill 150ms ease-out, strikethrough 200ms, row slide-out 300ms ease-in (after 800ms delay)
    - Detail panel open: slide-in 200ms ease-out
    - Detail panel close: slide-out 150ms ease-in
    - Sidebar hover: background fade 100ms
    - Drag: picked-up item scales 1.02, 5px shadow, 150ms
    - Theme toggle: cross-fade 200ms
  </animations>
</aesthetic_guidelines>

<security_considerations>
  <data_protection>
    - All data stored locally in IndexedDB — no data leaves the browser
    - No analytics, no tracking, no external requests after initial load
    - CRITICAL: Sanitize task title and notes before rendering (XSS prevention for any future import features)
  </data_protection>
  <input_validation>
    - Max title length: 500 chars (enforced in Dexie schema + UI)
    - Max notes length: 5000 chars
    - Project name: max 100 chars
    - Strip any HTML tags from all text inputs
  </input_validation>
</security_considerations>

<advanced_functionality>
  <theme_switching>
    - Toggle in sidebar footer
    - Reads system preference on first visit (prefers-color-scheme)
    - Persists choice to localStorage key "taskflow-theme"
    - Values: "light", "dark", "system"
  </theme_switching>

  <undo_complete>
    - When task is completed, show "Undo" toast for 800ms before hiding task
    - Click undo → task reappears, completed = false
  </undo_complete>
</advanced_functionality>

<final_integration_test>
  <test_scenario_1>
    <description>Create a project and add tasks with due dates</description>
    <steps>
      1. Open app — verify "Today" view loads with empty state
      2. Click "Add Project" in sidebar → type "Work" → Enter
      3. Verify "Work" appears in sidebar with blue dot and count "0"
      4. Click "Work" project → verify empty state shows
      5. Press "n" → type "Prepare presentation" → Enter
      6. Click task to open detail panel
      7. Set due date to today, priority to High
      8. Verify task appears in Today view with red priority dot
      9. Press "n" → type "Send weekly report" → set due to tomorrow
      10. Navigate to Upcoming view → verify both tasks appear under correct date headers
    </steps>
  </test_scenario_1>

  <test_scenario_2>
    <description>Complete tasks and verify state</description>
    <steps>
      1. From Today view, click checkbox on "Prepare presentation"
      2. Verify checkbox fills green, title gets strikethrough
      3. Verify "Undo" toast appears
      4. Wait 800ms → verify task disappears from Today view
      5. Navigate to "Work" project → verify completed task is hidden
      6. Verify sidebar count for "Work" decrements to 1
      7. Refresh browser → verify completed state persists
      8. Verify "All caught up!" empty state appears in Today view if no other tasks due
    </steps>
  </test_scenario_2>

  <test_scenario_3>
    <description>Keyboard navigation and shortcuts</description>
    <steps>
      1. Press Cmd+1 → verify Today view activates
      2. Press "n" → verify inline add input focuses
      3. Type "Quick task" → Enter → verify task created
      4. Press ↓ to select task → verify highlight
      5. Press "1" → verify priority set to None (no dot)
      6. Press "3" → verify priority set to Medium (amber dot)
      7. Press "t" → verify due date set to today
      8. Press Space → verify task completed
      9. Press Escape → verify detail panel closes
    </steps>
  </test_scenario_3>
</final_integration_test>

<success_criteria>
  <functionality>
    - All CRUD operations for tasks and projects work correctly
    - Smart views (Today, Upcoming, All) show correct filtered results
    - Drag-and-drop reordering persists after refresh
    - Keyboard shortcuts work for all documented actions
    - Theme toggle works and persists preference
  </functionality>
  <user_experience>
    - Initial load under 1.5s on 3G throttling
    - Task creation (keystroke to visible) under 50ms
    - Smooth 60fps drag animations
    - All interactive elements have visible focus indicators
  </user_experience>
  <technical_quality>
    - Zero TypeScript errors in strict mode
    - All components properly typed with explicit prop interfaces
    - No console errors or warnings in production build
  </technical_quality>
  <build>
    - npm run build produces working static files
    - Works on Chrome 80+, Firefox 78+, Safari 14+
    - Deployable to any static host (Netlify, Vercel, GitHub Pages)
  </build>
</success_criteria>

<build_output>
  <build_command>npm run build</build_command>
  <output_directory>dist/</output_directory>
  <contents>index.html + JS/CSS bundles, deployable to any static host</contents>
</build_output>

<key_implementation_notes>
  <critical_paths>
    1. Dexie.js database schema and reactive queries — foundation for all data
    2. Task list with drag-and-drop — core interaction pattern
    3. Smart view filtering logic — must be correct for usability
  </critical_paths>
  <recommended_implementation_order>
    1. Project setup (Vite + React + Tailwind + TypeScript)
    2. Dexie database schema + seed data
    3. App shell layout (sidebar + main panel)
    4. Task CRUD (create, read, update, delete)
    5. Project CRUD and sidebar navigation
    6. Smart views (Today, Upcoming, All)
    7. Task detail panel (slide-in)
    8. Drag-and-drop reordering
    9. Keyboard shortcuts
    10. Theme toggle (light/dark)
    11. Responsive design (mobile adaptations)
    12. Polish: animations, empty states, edge cases
  </recommended_implementation_order>
  <database_schema>
    ```typescript
    import Dexie, { type EntityTable } from 'dexie';
    import type { Task, Project } from '@/types';

    const db = new Dexie('TaskFlowDB') as Dexie & {
      tasks: EntityTable<Task, 'id'>;
      projects: EntityTable<Project, 'id'>;
    };

    db.version(1).stores({
      tasks: 'id, [projectId+sortOrder], dueDate, completed',
      projects: 'id, sortOrder',
    });

    export { db };
    ```
  </database_schema>
</key_implementation_notes>

</project_specification>
```
