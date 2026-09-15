"use client";

import { LayoutDashboard, Image as ImageIcon, Boxes, ListChecks, Settings } from "lucide-react";

interface SidebarNavItem {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
}


const NAV_ITEMS: SidebarNavItem[] = [
  { label: "Overview", href: "/dashboard", icon: LayoutDashboard },
  { label: "Datasets", href: "/dashboard/datasets", icon: ImageIcon },
  { label: "Models", href: "/dashboard/models", icon: Boxes },
  { label: "Annotations", href: "/dashboard/annotations", icon: ListChecks },
  { label: "Settings", href: "/dashboard/settings", icon: Settings },
];


export default function Sidebar({ recentThumbnails = [] }) {
  const slots = Array.from({ length: 4 }, (_, i) => recentThumbnails[i]);

  return (
    <aside className="relative flex h-full w-60 shrink-0 flex-col overflow-hidden border-r border-neutral-200 bg-neutral-50">
      <div className="flex flex-col gap-3 px-4 pt-6">
        {slots.map((thumb, i) =>
          thumb ? (
            <img
              key={i}
              src={thumb.training_img}
              alt={thumb.image_name}
              className="h-12 w-12 rounded-md scale-120 object-cover ring-1 ring-black/5"
            />
          ) : (
            <div key={i} className="h-12 w-12 rounded-md bg-neutral-200" aria-hidden />
          )
        )}
      </div>

      <nav className="mt-8 flex flex-col gap-1 px-3" aria-label="Dashboard">
        {NAV_ITEMS.map(({ label, href, icon: Icon }) => (
          <a
            key={href}
            href={href}
            className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-neutral-600 transition-colors hover:bg-neutral-200/70 hover:text-neutral-900"
          >
            <Icon className="h-4 w-4 shrink-0" />
            <span className="truncate">{label}</span>
          </a>
        ))}
      </nav>

    </aside>
  );
}