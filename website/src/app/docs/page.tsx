"use client";

import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import styles from "./Docs.module.css";
import { useEffect, useRef } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { ChevronRight, Cpu, ShieldCheck, Database, Settings } from "lucide-react";

export default function Docs() {
  const containerRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    gsap.registerPlugin(ScrollTrigger);
    
    // Select all sections to animate
    const sections = gsap.utils.toArray<HTMLElement>(`.${styles.section}`);
    
    sections.forEach((sec) => {
      gsap.fromTo(sec,
        { y: 50, opacity: 0 },
        {
          y: 0,
          opacity: 1,
          duration: 0.8,
          ease: "power3.out",
          scrollTrigger: {
            trigger: sec,
            start: "top 80%",
            toggleActions: "play none none reverse"
          }
        }
      );
    });
  }, []);

  return (
    <main className={styles.docsPage}>
      <Navbar />
      
      <div className={`container ${styles.docsContainer}`} ref={containerRef}>
        <aside className={styles.sidebar}>
          <div className={styles.sidebarSticky}>
            <h3 className={styles.sidebarTitle}>Documentation</h3>
            <ul className={styles.sidebarNav}>
              <li><a href="#quick-start" className="hoverable">Quick Start</a></li>
              <li><a href="#how-it-works" className="hoverable">How It Works</a></li>
              <li><a href="#cli-commands" className="hoverable">CLI Commands</a></li>
              <li><a href="#configuration" className="hoverable">Configuration</a></li>
              <li><a href="#supported-llms" className="hoverable">Supported LLMs</a></li>
            </ul>
          </div>
        </aside>

        <article className={styles.content}>
          <div className={styles.header}>
            <h1 className="h1">AutoHeal AI Documentation</h1>
            <p className="p-large">Autonomous Self-Healing Software Engine — Install once, self-heal forever.</p>
          </div>

          <section id="quick-start" className={styles.section}>
            <h2 className="h2">Quick Start</h2>
            
            <div className={styles.card}>
              <h3>1. Install</h3>
              <p>Install AutoHeal globally on your system using pipx or pip:</p>
              <pre><code>pip install autoheal-ai</code></pre>
            </div>

            <div className={styles.card}>
              <h3>2. Setup</h3>
              <p>Initialize AutoHeal inside your project folder and configure your API key.</p>
              <pre><code>{`# Initialize in your project
cd your-project/
autoheal init

# Set your LLM API key (OpenAI is default)
autoheal config set llm.api_key sk-proj-your-key-here

# (Optional) Use a different provider
autoheal config set llm.provider anthropic  # or google, ollama`}</code></pre>
            </div>

            <div className={styles.card}>
              <h3>3. Run</h3>
              <p>Prefix any normal command with <code>autoheal run</code>.</p>
              <pre><code>{`autoheal run "python app.py"
autoheal run "npm start"
autoheal run "go run main.go"
autoheal run "cargo run"`}</code></pre>
            </div>
          </section>

          <section id="how-it-works" className={styles.section}>
            <h2 className="h2">How It Works</h2>
            <p className="p-large" style={{marginBottom: "32px"}}>
              AutoHeal acts as a wrapper around your process, analyzing standard error outputs in real-time.
            </p>

            <div className={styles.architectureDiagram}>
              <div className={styles.archRow}>
                <div className={styles.archBox}><SearchIcon /> <span>Sentinel<br/><small>(Detect)</small></span></div>
                <ChevronRight className={styles.archArrow} />
                <div className={styles.archBox}><Cpu /> <span>CECE<br/><small>(Context)</small></span></div>
                <ChevronRight className={styles.archArrow} />
                <div className={styles.archBox}><Database /> <span>Diagnostics<br/><small>(Root Cause)</small></span></div>
              </div>
              
              <div className={styles.archRow} style={{ marginTop: "24px" }}>
                <div className={styles.archBox}><Database /> <span>Memory<br/><small>(Learn)</small></span></div>
                <ChevronRight className={styles.archArrow} style={{ transform: "rotate(180deg)" }} />
                <div className={styles.archBox}><ShieldCheck /> <span>Harness<br/><small>(Safety)</small></span></div>
                <ChevronRight className={styles.archArrow} style={{ transform: "rotate(180deg)" }} />
                <div className={styles.archBox}><Settings /> <span>Resolution<br/><small>(Fix)</small></span></div>
              </div>
            </div>

            <ol className={styles.stepsList}>
              <li><strong>Sentinel</strong> watches your process output for errors.</li>
              <li><strong>CECE</strong> builds full context (source code, environment, dependencies).</li>
              <li><strong>Diagnostics</strong> determines root cause via pattern matching + AI.</li>
              <li><strong>Resolution</strong> generates the appropriate fix (code patch, dependency install).</li>
              <li><strong>Harness</strong> checks safety gates before applying (requires user approval for code).</li>
              <li><strong>Memory</strong> stores the resolution for future instant fixes.</li>
            </ol>
          </section>

          <section id="cli-commands" className={styles.section}>
            <h2 className="h2">CLI Commands</h2>
            <div className={styles.tableWrapper}>
              <table>
                <thead>
                  <tr>
                    <th>Command</th>
                    <th>Description</th>
                  </tr>
                </thead>
                <tbody>
                  <tr><td><code>autoheal init [path]</code></td><td>Initialize AutoHeal in a project</td></tr>
                  <tr><td><code>autoheal run &lt;cmd&gt;</code></td><td>Run and monitor a command</td></tr>
                  <tr><td><code>autoheal status</code></td><td>Show error statistics</td></tr>
                  <tr><td><code>autoheal history [-n 20]</code></td><td>Show fix history</td></tr>
                  <tr><td><code>autoheal config list</code></td><td>Show all configuration</td></tr>
                  <tr><td><code>autoheal config set &lt;k&gt; &lt;v&gt;</code></td><td>Set a config value</td></tr>
                  <tr><td><code>autoheal config get &lt;k&gt;</code></td><td>Get a config value</td></tr>
                  <tr><td><code>autoheal diagnose &lt;err&gt;</code></td><td>Manually diagnose an error</td></tr>
                  <tr><td><code>autoheal version</code></td><td>Show version</td></tr>
                </tbody>
              </table>
            </div>
          </section>

          <section id="configuration" className={styles.section}>
            <h2 className="h2">Configuration</h2>
            <p>AutoHeal stores configuration locally in <code>.autoheal/config.toml</code>:</p>
            <pre><code>{`[llm]
provider = "openai"           # openai, anthropic, google, ollama
model = ""                    # Auto-selects best model per provider
api_key = "sk-proj-..."       # Your API key
temperature = 0.2

[resolution]
confidence_threshold = 0.75   # Min confidence for auto-fix
code_patch_threshold = 0.90   # Min confidence to suggest code patch
create_backup = true          # Git backup before patches

[general]
mode = "auto"                 # auto, suggest, manual
verbose = false`}</code></pre>
          </section>

          <section id="supported-llms" className={styles.section}>
            <h2 className="h2">Supported LLM Providers</h2>
            <div className={styles.tableWrapper}>
              <table>
                <thead>
                  <tr>
                    <th>Provider</th>
                    <th>Model</th>
                    <th>Setup Command</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><strong>OpenAI</strong> (default)</td>
                    <td>GPT-4o</td>
                    <td><code>autoheal config set llm.api_key sk-...</code></td>
                  </tr>
                  <tr>
                    <td><strong>Anthropic</strong></td>
                    <td>Claude 3.5 Sonnet</td>
                    <td><code>autoheal config set llm.provider anthropic</code></td>
                  </tr>
                  <tr>
                    <td><strong>Google</strong></td>
                    <td>Gemini 2.0 Flash</td>
                    <td><code>autoheal config set llm.provider google</code></td>
                  </tr>
                  <tr>
                    <td><strong>Ollama</strong> (local)</td>
                    <td>Llama 3.1</td>
                    <td><code>autoheal config set llm.provider ollama</code></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>
        </article>
      </div>

      <Footer />
    </main>
  );
}

function SearchIcon() {
  return <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>;
}
