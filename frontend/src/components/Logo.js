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
      {/* Outer circle background - Saffron gradient */}
      <circle cx="50" cy="50" r="48" fill="url(#gradient1)" />
      
      {/* Bowl shape - Cream/terracotta */}
      <path 
        d="M25 45 Q25 65 50 70 Q75 65 75 45 L25 45 Z" 
        fill="#C65D3B" 
        opacity="0.85"
      />
      <path 
        d="M25 45 L75 45 L73 47 L27 47 Z" 
        fill="#8B4513" 
        opacity="0.3"
      />
      
      {/* Steam lines - White with subtle shadow for visibility */}
      <path 
        d="M35 35 Q33 28 35 22" 
        stroke="#FFFFFF" 
        strokeWidth="3" 
        strokeLinecap="round"
        opacity="0.9"
        filter="url(#steam-glow)"
      />
      <path 
        d="M50 32 Q48 25 50 18" 
        stroke="#FFFFFF" 
        strokeWidth="3" 
        strokeLinecap="round"
        opacity="0.95"
        filter="url(#steam-glow)"
      />
      <path 
        d="M65 35 Q67 28 65 22" 
        stroke="#FFFFFF" 
        strokeWidth="3" 
        strokeLinecap="round"
        opacity="0.9"
        filter="url(#steam-glow)"
      />
      
      {/* Food elements in bowl - Indian-inspired colors */}
      <circle cx="40" cy="52" r="4" fill="#7CB342" opacity="0.8" /> {/* Green veggies */}
      <circle cx="52" cy="50" r="3.5" fill="#F4D03F" opacity="0.75" /> {/* Turmeric */}
      <circle cx="60" cy="53" r="3" fill="#FFF8E7" opacity="0.9" /> {/* Cream */}
      <circle cx="45" cy="58" r="3" fill="#FFB74D" opacity="0.7" /> {/* Golden */}
      
      {/* Soup surface - Creamy */}
      <ellipse cx="50" cy="45" rx="24" ry="3" fill="#FFF8E7" opacity="0.4" />
      
      {/* Gradient and filter definitions */}
      <defs>
        <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#D4AF37" />
          <stop offset="50%" stopColor="#E8B84D" />
          <stop offset="100%" stopColor="#F4D03F" />
        </linearGradient>
        <filter id="steam-glow">
          <feGaussianBlur stdDeviation="0.5" result="coloredBlur"/>
          <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>
    </svg>
  );
};

export default Logo;
