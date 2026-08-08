"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import styles from "./Cursor.module.css";

export default function Cursor() {
  const cursorRef = useRef<HTMLDivElement>(null);
  const followerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const cursor = cursorRef.current;
    const follower = followerRef.current;
    
    if (!cursor || !follower) return;

    // Fast movement for the dot
    const onMouseMove = (e: MouseEvent) => {
      gsap.to(cursor, {
        x: e.clientX,
        y: e.clientY,
        duration: 0.1,
        ease: "power2.out"
      });
      
      // Slower lagging movement for the outer ring
      gsap.to(follower, {
        x: e.clientX,
        y: e.clientY,
        duration: 0.5,
        ease: "power2.out"
      });
    };

    const onMouseEnter = () => {
      gsap.to(cursor, { scale: 0, opacity: 0, duration: 0.2 });
      gsap.to(follower, { scale: 2.5, backgroundColor: "rgba(255,255,255,0.1)", duration: 0.3 });
    };

    const onMouseLeave = () => {
      gsap.to(cursor, { scale: 1, opacity: 1, duration: 0.2 });
      gsap.to(follower, { scale: 1, backgroundColor: "transparent", duration: 0.3 });
    };

    window.addEventListener("mousemove", onMouseMove);

    // Attach hover events to links and buttons
    const attachHoverEvents = () => {
      const interactables = document.querySelectorAll("a, button, input, textarea, .hoverable");
      interactables.forEach((el) => {
        el.addEventListener("mouseenter", onMouseEnter);
        el.addEventListener("mouseleave", onMouseLeave);
      });
    };

    // Small delay to ensure DOM is ready
    setTimeout(attachHoverEvents, 500);

    return () => {
      window.removeEventListener("mousemove", onMouseMove);
      const interactables = document.querySelectorAll("a, button, input, textarea, .hoverable");
      interactables.forEach((el) => {
        el.removeEventListener("mouseenter", onMouseEnter);
        el.removeEventListener("mouseleave", onMouseLeave);
      });
    };
  }, []);

  return (
    <>
      <div ref={cursorRef} className={styles.cursor}></div>
      <div ref={followerRef} className={styles.follower}></div>
    </>
  );
}
