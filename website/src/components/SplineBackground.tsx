"use client";

import Spline from '@splinetool/react-spline';
import { useEffect, useState } from 'react';

export default function SplineBackground() {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  if (!isClient) return <div className="spline-placeholder" />;

  return (
    <div className="spline-container">
      {/* 
        This is a beautiful abstract 3D dark-mode placeholder Spline scene from the community. 
        It provides a sleek premium feel for the hero section.
      */}
      <Spline scene="https://prod.spline.design/6Wq1Q7YGyM-iab9i/scene.splinecode" />
      
      <style jsx>{`
        .spline-container {
          position: absolute;
          top: 0;
          left: 0;
          width: 100vw;
          height: 100vh;
          z-index: 1;
          opacity: 0.6;
          pointer-events: none; /* Let clicks pass through to UI */
        }
        .spline-placeholder {
          position: absolute;
          top: 0;
          left: 0;
          width: 100vw;
          height: 100vh;
          background: radial-gradient(circle at 50% 50%, rgba(37, 99, 235, 0.1) 0%, var(--background) 100%);
          z-index: 1;
        }
      `}</style>
    </div>
  );
}
