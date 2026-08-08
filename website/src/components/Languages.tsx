"use client";

import { Swiper, SwiperSlide } from "swiper/react";
import { Autoplay, EffectCards } from "swiper/modules";
import "swiper/css";
import "swiper/css/effect-cards";
import styles from "./Languages.module.css";
import { Terminal } from "lucide-react";

const examples = [
  { lang: "Python", code: 'autoheal run "python app.py"', color: "#3776AB" },
  { lang: "Node.js", code: 'autoheal run "npm start"', color: "#339933" },
  { lang: "Go", code: 'autoheal run "go run main.go"', color: "#00ADD8" },
  { lang: "Rust", code: 'autoheal run "cargo run"', color: "#DEA584" },
  { lang: "Ruby", code: 'autoheal run "ruby script.rb"', color: "#CC342D" },
];

export default function Languages() {
  return (
    <section id="install" className={`section ${styles.languagesSection}`}>
      <div className={`container ${styles.container}`}>
        <div className={styles.content}>
          <h2 className="h2">Language Agnostic.</h2>
          <p className="p-large">
            AutoHeal AI sits at the terminal level. It doesn't care what language you write in. If it outputs to standard error, AutoHeal can fix it.
          </p>
          <div className={styles.installBox}>
            <p className={styles.installLabel}>Install Globally via Pipx:</p>
            <code className={styles.codeBlock}>pipx install autoheal-ai</code>
          </div>
        </div>

        <div className={styles.sliderContainer}>
          <Swiper
            effect={"cards"}
            grabCursor={true}
            modules={[EffectCards, Autoplay]}
            autoplay={{ delay: 2500, disableOnInteraction: false }}
            className={styles.swiper}
          >
            {examples.map((ex, idx) => (
              <SwiperSlide key={idx} className={styles.slide} style={{ borderTop: `4px solid ${ex.color}` }}>
                <div className={styles.slideHeader}>
                  <Terminal size={20} color={ex.color} />
                  <span>{ex.lang}</span>
                </div>
                <div className={styles.slideBody}>
                  <code>{ex.code}</code>
                </div>
              </SwiperSlide>
            ))}
          </Swiper>
        </div>
      </div>
    </section>
  );
}
