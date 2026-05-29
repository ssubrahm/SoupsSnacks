import React from 'react';

/** Jeeves — gold monogram J + bow tie on dark medallion (variant B). */
const JeevesIcon = ({ size = 20, className = '', title = 'Jeeves — at your service' }) => (
  <svg
    className={`jeeves-icon ${className}`.trim()}
    width={size}
    height={size}
    viewBox="0 0 48 48"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    role="img"
    aria-label={title}
  >
    <title>{title}</title>
    <circle cx="24" cy="24" r="22" fill="#1A1410" stroke="#D4AF37" strokeWidth="2.5" />
    <text
      x="24"
      y="30"
      textAnchor="middle"
      fill="#E8B84D"
      fontFamily="Georgia, 'Times New Roman', serif"
      fontSize="26"
      fontWeight="700"
    >
      J
    </text>
    <path fill="#E8B84D" d="M17 34 L14 36 L17 38 L24 36 L31 38 L34 36 L31 34 L24 36 Z" />
  </svg>
);

export default JeevesIcon;
