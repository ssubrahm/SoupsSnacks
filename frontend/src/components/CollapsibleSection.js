import React, { useState } from 'react';
import './CollapsibleSection.css';

/**
 * Finder-style collapsible panel for reclaiming vertical space.
 */
const CollapsibleSection = ({
  title,
  subtitle,
  badge,
  defaultOpen = true,
  storageKey,
  className = '',
  children,
}) => {
  const [open, setOpen] = useState(() => {
    if (storageKey) {
      const saved = localStorage.getItem(storageKey);
      if (saved !== null) {
        return saved === 'true';
      }
    }
    return defaultOpen;
  });

  const toggle = () => {
    const next = !open;
    setOpen(next);
    if (storageKey) {
      localStorage.setItem(storageKey, String(next));
    }
  };

  return (
    <section
      className={`collapsible-section ${open ? 'is-open' : 'is-collapsed'} ${className}`.trim()}
    >
      <button
        type="button"
        className="collapsible-header"
        onClick={toggle}
        aria-expanded={open}
      >
        <span className="collapsible-chevron" aria-hidden="true">
          {open ? '▼' : '▶'}
        </span>
        <span className="collapsible-title-group">
          <span className="collapsible-title">{title}</span>
          {subtitle && !open && (
            <span className="collapsible-subtitle">{subtitle}</span>
          )}
        </span>
        {badge && <span className="collapsible-badge">{badge}</span>}
      </button>
      <div className="collapsible-body" hidden={!open}>
        {children}
      </div>
    </section>
  );
};

export default CollapsibleSection;
