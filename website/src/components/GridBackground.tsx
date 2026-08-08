"use client";

import { useEffect, useState } from "react";
import styles from "./GridBackground.module.css";

export default function GridBackground() {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };

    // Track mouse globally for the spotlight effect
    window.addEventListener("mousemove", handleMouseMove);
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
    };
  }, []);

  return (
    <div className={styles.gridWrapper}>
      {/* The base repeating grid pattern */}
      <div className={styles.gridPattern} />
      
      {/* The interactive radial spotlight that follows the mouse cursor */}
      <div 
        className={styles.spotlight} 
        style={{
          background: `radial-gradient(800px circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(37, 99, 235, 0.15), transparent 40%)`,
        }}
      />
    </div>
  );
}
