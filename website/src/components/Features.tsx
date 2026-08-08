"use client";

import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import styles from "./Features.module.css";
import { Search, Cpu, CheckCircle } from "lucide-react";

gsap.registerPlugin(ScrollTrigger);

const features = [
  {
    title: "Real-time Sentinel",
    description: "Monitors your application's stdout/stderr in real-time, detecting crashes across 8+ languages before you even notice them.",
    icon: <Search className={styles.icon} size={32} />
  },
  {
    title: "AI Diagnostics",
    description: "Extracts full context, reads your source code, and uses advanced LLMs to identify the precise root cause of the error.",
    icon: <Cpu className={styles.icon} size={32} />
  },
  {
    title: "Autonomous Resolution",
    description: "Generates code patches, fixes dependencies, or restarts processes automatically based on safety confidence thresholds.",
    icon: <CheckCircle className={styles.icon} size={32} />
  }
];

export default function Features() {
  const sectionRef = useRef<HTMLElement>(null);
  const cardsRef = useRef<(HTMLDivElement | null)[]>([]);

  useEffect(() => {
    cardsRef.current.forEach((card, index) => {
      if (card) {
        gsap.fromTo(card, 
          { y: 100, opacity: 0 },
          { 
            y: 0, 
            opacity: 1, 
            duration: 0.8, 
            ease: "power3.out",
            scrollTrigger: {
              trigger: card,
              start: "top 85%",
              toggleActions: "play none none reverse"
            }
          }
        );
      }
    });
  }, []);

  return (
    <section id="how-it-works" ref={sectionRef} className={`section ${styles.featuresSection}`}>
      <div className="container">
        <div className={styles.header}>
          <h2 className="h2">How AutoHeal works</h2>
          <p className="p-large">From crash to fix in milliseconds.</p>
        </div>
        
        <div className={styles.grid}>
          {features.map((feature, i) => (
            <div 
              key={i} 
              ref={(el) => { cardsRef.current[i] = el; }} 
              className={`glass-panel hoverable ${styles.card}`}
            >
              <div className={styles.iconWrapper}>
                {feature.icon}
              </div>
              <h3 className={styles.cardTitle}>{feature.title}</h3>
              <p className={styles.cardDesc}>{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
