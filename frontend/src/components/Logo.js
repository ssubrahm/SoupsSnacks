import React from 'react';

const Logo = ({ size = 40 }) => {
  return (
    <svg 
      width={size} 
      height={size} 
      viewBox="0 0 100 100" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
      style={{ display: 'inline-block', verticalAlign: 'middle' }}
    >
      {/* Outer circle background */}
      <circle cx="50" cy="50" r="48" fill="url(#gradient1)" />
      
      {/* Bowl shape */}
      <path 
        d="M25 45 Q25 65 50 70 Q75 65 75 45 L25 45 Z" 
        fill="#FFF" 
        opacity="0.95"
      />
      
      {/* Steam lines */}
      <path 
        d="M35 35 Q33 28 35 22" 
        stroke="#FFB84D" 
        strokeWidth="2.5" 
        strokeLinecap="round"
        opacity="0.8"
      />
      <path 
        d="M50 32 Q48 25 50 18" 
        stroke="#FFB84D" 
        strokeWidth="2.5" 
        strokeLinecap="round"
        opacity="0.9"
      />
      <path 
        d="M65 35 Q67 28 65 22" 
        stroke="#FFB84D" 
        strokeWidth="2.5" 
        strokeLinecap="round"
        opacity="0.8"
      />
      
      {/* Food elements in bowl */}
      <circle cx="40" cy="52" r="4" fill="#FF6B6B" opacity="0.7" />
      <circle cx="52" cy="50" r="3.5" fill="#4ECDC4" opacity="0.7" />
      <circle cx="60" cy="53" r="3" fill="#95E1D3" opacity="0.7" />
      <circle cx="45" cy="58" r="3" fill="#FFE66D" opacity="0.7" />
      
      {/* Soup surface */}
      <ellipse cx="50" cy="45" rx="24" ry="3" fill="#FFF" opacity="0.3" />
      
      {/* Gradient definitions */}
      <defs>
        <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#FF6B6B" />
          <stop offset="50%" stopColor="#FF8E53" />
          <stop offset="100%" stopColor="#FFA940" />
        </linearGradient>
      </defs>
    </svg>
  );
};

export default Logo;
