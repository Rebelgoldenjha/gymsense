const pptxgen = require('pptxgenjs');

async function createDeck() {
    const pres = new pptxgen();

    // ============================================================
    // THEME: Coral Energy (fitness/energy vibe)
    // ============================================================
    const THEME = {
        name: "GYMSENSE_CoralEnergy",
        headFontFace: "Cambria",
        bodyFontFace: "Calibri",
        colors: {
            dk1: "2F3C7E", // Navy (dark text)
            lt1: "FFFFFF", // White (light bg)
            dk2: "F96167", // Coral (primary brand)
            lt2: "F9E795", // Gold (secondary)
            accent1: "F96167", // Coral
            accent2: "F9E795", // Gold
            accent3: "2F3C7E", // Navy
            accent4: "065A82", // Deep Blue
            accent5: "1C7293", // Teal
            accent6: "FFFFFF", // White
            hlink: "F96167",
            folHlink: "F9E795"
        }
    };

    // Apply theme colors
    pres.defineTheme({ name: THEME.name, theme: THEME });
    pres.theme = THEME.name;
    pres.layout = "LAYOUT_16x9"; // 10" x 5.625"j

    // ============================================================
    // DEFINE SLIDE MASTERS (LAYOUTS)
    // ============================================================

    // Master slide with footer
    pres.defineSlideMaster({
        name: "MASTER_SLIDE",
        title: "Master",
        background: { color: "FFFFFF" },
        objects: [
            // Footer bar
            {
                shape: "RECTANGLE",
                x: 0,
                y: 5.2,
                w: 10,
                h: 0.425,
                fill: { color: "F5F5F5" },
                line: { color: "E0E0E0", pt: 1 }
            },
            {
                text: "GYMSENSE  |  Startup Bihar Pitch  |  Confidential",
                options: {
                    x: 0.5,
                    y: 5.25,
                    w: 9,
                    h: 0.35,
                    fontFace: "Calibri",
                    fontSize: 9,
                    color: "888888",
                    align: "left"
                }
            },
            {
                text: "Slide {slideNumber}",
                options: {
                    x: 9.2,
                    y: 5.25,
                    w: 0.6,
                    h: 0.35,
                    fontFace: "Calibri",
                    fontSize: 9,
                    color: "888888",
                    align: "right"
                }
            }
        ],
        slideNumber: { x: 9.2, y: 5.25, w: 0.6, h: 0.35 }
    });

    // Title slide layout (dark bg)
    pres.defineSlideMaster({
        name: "TITLE_SLIDE",
        title: "Title Slide",
        background: { color: "2F3C7E" },
        objects: [{
                text: "{{title}}",
                options: {
                    placeholder: "title",
                    x: 1,
                    y: 1.5,
                    w: 8,
                    h: 1.5,
                    fontFace: "Cambria",
                    fontSize: 44,
                    bold: true,
                    color: "FFFFFF",
                    align: "center"
                }
            },
            {
                text: "{{body}}",
                options: {
                    placeholder: "body",
                    x: 1,
                    y: 3.2,
                    w: 8,
                    h: 1,
                    fontFace: "Calibri",
                    fontSize: 22,
                    color: "F9E795",
                    align: "center"
                }
            },
            {
                text: "GYMSENSE",
                options: {
                    x: 1,
                    y: 4.8,
                    w: 8,
                    h: 0.5,
                    fontFace: "Cambria",
                    fontSize: 18,
                    bold: true,
                    color: "F96167",
                    align: "center"
                }
            }
        ]
    });

    // Section divider layout
    pres.defineSlideMaster({
        name: "SECTION_DIVIDER",
        title: "Section Divider",
        background: { color: "F96167" },
        objects: [{
                text: "{{title}}",
                options: {
                    placeholder: "title",
                    x: 1,
                    y: 2,
                    w: 8,
                    h: 1,
                    fontFace: "Cambria",
                    fontSize: 40,
                    bold: true,
                    color: "FFFFFF",
                    align: "center"
                }
            },
            {
                text: "{{body}}",
                options: {
                    placeholder: "body",
                    x: 1,
                    y: 3.2,
                    w: 8,
                    h: 0.8,
                    fontFace: "Calibri",
                    fontSize: 20,
                    color: "FFFFFF",
                    align: "center",
                    opacity: 0.9
                }
            }
        ]
    });

    // Content layout
    pres.defineSlideMaster({
        name: "CONTENT_SLIDE",
        title: "Content Slide",
        background: { color: "FFFFFF" },
        objects: [{
                text: "{{title}}",
                options: {
                    placeholder: "title",
                    x: 0.5,
                    y: 0.4,
                    w: 9,
                    h: 0.8,
                    fontFace: "Cambria",
                    fontSize: 36,
                    bold: true,
                    color: "2F3C7E",
                    align: "left"
                }
            },
            {
                text: "{{body}}",
                options: {
                    placeholder: "body",
                    x: 0.5,
                    y: 1.4,
                    w: 9,
                    h: 3.5,
                    fontFace: "Calibri",
                    fontSize: 16,
                    color: "2F3C7E",
                    align: "left"
                }
            }
        ]
    });

    // ============================================================
    // SLIDE 1: TITLE SLIDE
    // ============================================================
    let slide = pres.addSlide({ masterName: "TITLE_SLIDE" });
    slide.addText("GYMSENSE", {
        placeholder: "title",
        fontFace: "Cambria",
        fontSize: 48,
        bold: true,
        color: "FFFFFF",
        align: "center"
    });
    slide.addText("Your AI Form Coach in the Browser\nNo Hardware • No Wearable • Just Your Camera", {
        placeholder: "body",
        fontFace: "Calibri",
        fontSize: 22,
        color: "F9E795",
        align: "center"
    });
    slide.addText("Startup Bihar Pitch Deck  |  November 2026", {
        x: 1,
        y: 4.8,
        w: 8,
        h: 0.5,
        fontFace: "Cambria",
        fontSize: 16,
        color: "F96167",
        align: "center"
    });

    // ============================================================
    // SLIDE 2: EXECUTIVE SUMMARY
    // ============================================================
    slide = pres.addSlide({ masterName: "CONTENT_SLIDE", sectionTitle: "Executive Summary" });
    slide.addText("Executive Summary", {
        placeholder: "title",
        fontFace: "Cambria",
        fontSize: 36,
        bold: true,
        color: "2F3C7E"
    });

    slide.addText([
        { text: "The Problem: ", bold: true, color: "2F3C7E" },
        { text: "73% of home exercisers use incorrect form, risking injury and wasting effort. Personal trainers cost $150-300/mo. Free apps (Nike, YouTube) offer zero feedback.", color: "2F3C7E" }
    ], { x: 0.5, y: 1.4, w: 9, h: 0.8, fontFace: "Calibri", fontSize: 15, lineSpacing: 1.3 });

    slide.addText([
        { text: "The Solution: ", bold: true, color: "F96167" },
        { text: "GYMSENSE runs MediaPipe pose estimation in-browser. Select an exercise - camera auto-starts - 33 keypoints tracked - real-time joint angles - rep counting - instant form feedback (Knees caving - push out!). 7 exercises at launch.", color: "2F3C7E" }
    ], { x: 0.5, y: 2.2, w: 9, h: 0.8, fontFace: "Calibri", fontSize: 15, lineSpacing: 1.3 });

    slide.addText([
        { text: "The Pivot (Our Moat): ", bold: true, color: "065A82" },
        { text: "B2C fitness apps have 8% monthly churn and $45 CAC. We're building a B2B2C Trainer OS: trainers pay $50/mo for client management + AI form analysis; their clients get free access. Trainers become our distribution channel. Network effects + switching costs + data flywheel.", color: "2F3C7E" }
    ], { x: 0.5, y: 3.1, w: 9, h: 1, fontFace: "Calibri", fontSize: 15, lineSpacing: 1.3 });

    // Score cards
    const scores = [
        { label: "Uniqueness", value: "4/10", color: "F96167" },
        { label: "Scalability", value: "6/10", color: "F9E795" },
        { label: "Profitability", value: "5/10", color: "065A82" },
        { label: "Defensibility", value: "3/10 to 8/10*", color: "1C7293" },
        { label: "Execution", value: "4/10", color: "2F3C7E" }
    ];
    scores.forEach((s, i) => {
        slide.addText(s.value, { x: 0.5 + i * 1.85, y: 4.2, w: 1.6, h: 0.7, fontFace: "Cambria", fontSize: 28, bold: true, color: s.color, align: "center" });
        slide.addText(s.label, { x: 0.5 + i * 1.85, y: 4.85, w: 1.6, h: 0.4, fontFace: "Calibri", fontSize: 11, color: "2F3C7E", align: "center" });
    });
    slide.addText("*With Trainer Platform pivot", { x: 0.5, y: 5.0, w: 9, h: 0.3, fontFace: "Calibri", fontSize: 9, color: "888888", align: "center" });

    // ============================================================
    // SLIDE 3: PROBLEM VALIDATION
    // ============================================================
    slide = pres.addSlide({ masterName: "CONTENT_SLIDE", sectionTitle: "Problem Validation" });
    slide.addText("Problem Validation", {
        placeholder: "title",
        fontFace: "Cambria",
        fontSize: 36,
        bold: true,
        color: "2F3C7E"
    });

    const problems = [
        "73% of home exercisers use incorrect form (ACSM data)",
        "Form errors to injury (3.5M gym injuries/yr in US) + wasted reps",
        "Personal trainers: $150-300/mo - unaffordable for most",
        "Free apps (Nike Training Club, YouTube) = zero feedback loop",
        "Mirror/checking phone = subjective, inconsistent, no rep counting",
        "Pain is chronic (injury later), not acute - hard to sell urgency"
    ];
    problems.forEach((p, i) => {
        slide.addText(p, { x: 0.5, y: 1.3 + i * 0.55, w: 9, h: 0.5, fontFace: "Calibri", fontSize: 15, color: "2F3C7E", bullet: true, breakLine: true });
    });

    slide.addText("Verdict: Real problem, but 'nice-to-have' for most. Must-have only after injury.", { x: 0.5, y: 4.7, w: 9, h: 0.5, fontFace: "Calibri", fontSize: 14, bold: true, color: "F96167" });

    // ============================================================
    // SLIDE 4: TARGET AUDIENCE
    // ============================================================
    slide = pres.addSlide({ masterName: "CONTENT_SLIDE", sectionTitle: "Target Audience" });
    slide.addText("Target Audience", {
        placeholder: "title",
        fontFace: "Cambria",
        fontSize: 36,
        bold: true,
        color: "2F3C7E"
    });

    // Primary persona card
    slide.addText("PRIMARY: Marcus - Home Strength Enthusiast", { x: 0.5, y: 1.3, w: 4, h: 0.4, fontFace: "Cambria", fontSize: 18, bold: true, color: "F96167" });
    slide.addText([
        "Age 25-40, $75k+ HHI, remote/hybrid worker",
        "Owns dumbbells/kettlebells or bodyweight-only",
        "Works out 3-5x/week, follows programs",
        "Tried Peloton (too cardio), Freeletics (no form feedback)",
        "Willing to pay $12-20/mo for form confidence",
        "TAM: ~18M US | SAM: ~$2.5B (AI form-coaching niche)"
    ], { x: 0.5, y: 1.7, w: 4, h: 2.5, fontFace: "Calibri", fontSize: 13, color: "2F3C7E", bullet: true, breakLine: true, paraSpaceAfter: 4 });

    // Secondary
    slide.addText("SECONDARY: New Year Resolution Beginners", { x: 5, y: 1.3, w: 4, h: 0.4, fontFace: "Cambria", fontSize: 18, bold: true, color: "F9E795" });
    slide.addText([
        "Age 20-35, sporadic exercisers, high churn",
        "Price sensitive ($0-10/mo)",
        "Need habit formation + basic guidance",
        "TAM: ~35M US | Low LTV, high volume"
    ], { x: 5, y: 1.7, w: 4, h: 2, fontFace: "Calibri", fontSize: 13, color: "2F3C7E", bullet: true, breakLine: true, paraSpaceAfter: 4 });

    // Early adopters
    slide.addText("EARLY ADOPTERS: Quantified-Self / Biohackers", { x: 0.5, y: 3.8, w: 4, h: 0.4, fontFace: "Cambria", fontSize: 18, bold: true, color: "065A82" });
    slide.addText([
        "Track HRV, sleep, macros, now: form quality",
        "Willing to pay $20-30/mo for data",
        "TAM: ~2M US | High referral potential"
    ], { x: 0.5, y: 4.2, w: 4, h: 1.2, fontFace: "Calibri", fontSize: 13, color: "2F3C7E", bullet: true, breakLine: true, paraSpaceAfter: 4 });

    // B2B persona (the pivot)
    slide.addText("B2B PERSONA: Sarah - Independent Trainer", { x: 5, y: 3.8, w: 4, h: 0.4, fontFace: "Cambria", fontSize: 18, bold: true, color: "1C7293" });
    slide.addText([
        "300k+ certified trainers in US",
        "Capped at ~30 1:1 clients ($3k-6k/mo ceiling)",
        "No tools to scale form coaching",
        "Pays $50-100/mo for Trainer OS",
        "Brings 10-30 clients each = distribution"
    ], { x: 5, y: 4.2, w: 4, h: 1.8, fontFace: "Calibri", fontSize: 13, color: "2F3C7E", bullet: true, breakLine: true, paraSpaceAfter: 4 });

    // ============================================================
    // SLIDE 5: MARKET SIZE
    // ============================================================
    slide = pres.addSlide({ masterName: "CONTENT_SLIDE", sectionTitle: "Market Size" });
    slide.addText("Market Sizing", {
        placeholder: "title",
        fontFace: "Cambria",
        fontSize: 36,
        bold: true,
        color: "2F3C7E"
    });

    slide.addText([
        { text: "TAM (Global Digital Fitness): ", bold: true, color: "2F3C7E" },
        { text: "$59B (2023) to $140B (2030 CAGR 12.5%)", color: "2F3C7E" }
    ], { x: 0.5, y: 1.3, w: 9, h: 0.5, fontFace: "Calibri", fontSize: 16 });

    slide.addText([
        { text: "SAM (AI Form-Coaching Niche): ", bold: true, color: "F96167" },
        { text: "~$2.5B (3% of digital fitness, growing 25% YoY)", color: "2F3C7E" }
    ], { x: 0.5, y: 1.9, w: 9, h: 0.5, fontFace: "Calibri", fontSize: 16 });

    slide.addText([
        { text: "SOM (Realistic 5-Year Capture): ", bold: true, color: "065A82" },
        { text: "$5-15M ARR (0.2-0.6% SAM) with Trainer Platform", color: "2F3C7E" }
    ], { x: 0.5, y: 2.5, w: 9, h: 0.5, fontFace: "Calibri", fontSize: 16 });

    // Visual TAM/SAM/SOM - using simple text boxes
    slide.addText("TAM", { x: 1, y: 3.3, w: 2.5, h: 0.5, fontFace: "Cambria", fontSize: 14, bold: true, color: "FFFFFF", align: "center" });
    slide.addText("$140B", { x: 1, y: 3.7, w: 2.5, h: 0.6, fontFace: "Cambria", fontSize: 28, bold: true, color: "FFFFFF", align: "center" });

    slide.addText("SAM", { x: 3.75, y: 3.3, w: 2.5, h: 0.5, fontFace: "Cambria", fontSize: 14, bold: true, color: "FFFFFF", align: "center" });
    slide.addText("$2.5B", { x: 3.75, y: 3.7, w: 2.5, h: 0.6, fontFace: "Cambria", fontSize: 28, bold: true, color: "FFFFFF", align: "center" });

    slide.addText("SOM (5yr)", { x: 6.5, y: 3.3, w: 2.5, h: 0.5, fontFace: "Cambria", fontSize: 14, bold: true, color: "FFFFFF", align: "center" });
    slide.addText("$15M", { x: 6.5, y: 3.7, w: 2.5, h: 0.6, fontFace: "Cambria", fontSize: 28, bold: true, color: "FFFFFF", align: "center" });

    // Color the stat boxes
    [1, 3.75, 6.5].forEach(x => {
        slide.addShape("RECTANGLE", { x: x, y: 3.3, w: 2.5, h: 1.2, fill: { color: "2F3C7E" }, line: { color: "F96167", pt: 2 } });
    });

    // Move text to front
    slide.addText("TAM", { x: 1, y: 3.3, w: 2.5, h: 0.5, fontFace: "Cambria", fontSize: 14, bold: true, color: "FFFFFF", align: "center" });
    slide.addText("$140B", { x: 1, y: 3.7, w: 2.5, h: 0.6, fontFace: "Cambria", fontSize: 28, bold: true, color: "FFFFFF", align: "center" });
    slide.addText("SAM", { x: 3.75, y: 3.3, w: 2.5, h: 0.5, fontFace: "Cambria", fontSize: 14, bold: true, color: "FFFFFF", align: "center" });
    slide.addText("$2.5B", { x: 3.75, y: 3.7, w: 2.5, h: 0.6, fontFace: "Cambria", fontSize: 28, bold: true, color: "FFFFFF", align: "center" });
    slide.addText("SOM (5yr)", { x: 6.5, y: 3.3, w: 2.5, h: 0.5, fontFace: "Cambria", fontSize: 14, bold: true, color: "FFFFFF", align: "center" });
    slide.addText("$15M", { x: 6.5, y: 3.7, w: 2.5, h: 0.6, fontFace: "Cambria", fontSize: 28, bold: true, color: "FFFFFF", align: "center" });

    // ============================================================
    // SLIDE 6: TOP 10 COMPETITORS (TABLE)
    // ============================================================
    slide = pres.addSlide({ masterName: "CONTENT_SLIDE", sectionTitle: "Competitors" });
    slide.addText("Top 10 Competitors", {
        placeholder: "title",
        fontFace: "Cambria",
        fontSize: 36,
        bold: true,
        color: "2F3C7E"
    });

    const compHeaders = ["#", "Company", "Model", "Pricing", "Funding", "Revenue", "Users", "Gap They Leave"];
    const compRows = [
        ["1", "Tempo", "Hardware + Sub", "$395+ HW + $39/mo", "$220M", "~$100M", "~50k", "Portable/bodyweight; $400 barrier"],
        ["2", "Zenia", "Freemium App", "$14.99/mo", "$1.2M", "~$2M", "~200k", "Yoga/pilates only; no strength"],
        ["3", "Kaia Health", "B2B2C (Insurers)", "Free to patient", "$120M+", "~$50M", "600k+", "Clinical only; not for healthy users"],
        ["4", "Fitbod", "Sub (no camera)", "$12.99/mo", "$12M", "~$30M", "1M+", "No form feedback; no camera"],
        ["5", "Freeletics", "Freemium HIIT", "$11.99/mo", "$25M", "~$60M", "50M+ DL", "No camera form analysis"],
        ["6", "JuggernautAI", "Sub (powerlifting)", "$29.99/mo", "Bootstrapped", "~$5M", "~30k", "Niche; no form tech"],
        ["7", "Nike Training Club", "Free (brand)", "Free", "N/A", "N/A", "50M+", "No AI; no personalization"],
        ["8", "Mirror/Lululemon", "Hardware + Sub", "$995+ HW + $39/mo", "Acquired $500M", "~$150M", "~200k", "Class-based; trainer can't see you"],
        ["9", "Strong/Hevy", "Freemium Logger", "$5-8/mo", "Minimal", "~$3M", "2M+", "No AI; manual entry only"],
        ["10", "Caliber", "Human Remote Coach", "$199/mo", "$12M", "~$10M", "~5k", "Too expensive; doesn't scale"]
    ];

    const tableData = [compHeaders, ...compRows];
    slide.addTable(tableData, {
        x: 0.3,
        y: 1.1,
        w: 9.4,
        h: 4.2,
        fontFace: "Calibri",
        fontSize: 9.5,
        color: "2F3C7E",
        border: { pt: 1, color: "E0E0E0" },
        rowColors: ["2F3C7E", "FFFFFF", "FFF8F8"],
        headerRow: true,
        headerColor: "2F3C7E",
        headerFontColor: "FFFFFF",
        colWidths: [0.3, 1.2, 1.1, 1.1, 0.9, 0.9, 0.8, 2.1]
    });

    // ============================================================
    // SLIDE 7: MARKET GAP ANALYSIS
    // ============================================================
    slide = pres.addSlide({ masterName: "CONTENT_SLIDE", sectionTitle: "Market Gaps" });
    slide.addText("Market Gap Analysis: Where Competitors Miss", {
        placeholder: "title",
        fontFace: "Cambria",
        fontSize: 36,
        bold: true,
        color: "2F3C7E"
    });

    const gaps = [
        { gap: "No Duolingo for Form", evidence: "All competitors are: (a) hardware-gated $400+, (b) human-coach-gated $150+/mo, (c) no form feedback, or (d) single-modality (yoga only). Mass market wants <$20/mo, no hardware, strength + mobility.", size: "LARGE" },
        { gap: "Form Feedback for Compound Movements", evidence: "Tempo does this but requires hardware. Zenia only yoga. Kaia focuses on rehab, not performance. Squat/deadlift/bench = highest injury risk + highest demand.", size: "MEDIUM" },
        { gap: "Privacy-First Local Processing", evidence: "All cloud AI fitness apps upload video. GYMSENSE can run MediaPipe in-browser (WebAssembly) - zero video leaves device.", size: "GROWING" },
        { gap: "Travel/Zero-Equipment Mode", evidence: "Hardware solutions fail here. App solutions exist but lack form feedback. 60M+ business travelers/yr + hotel gym constraints.", size: "MEDIUM" },
        { gap: "Coach/Trainer Tools (B2B2C)", evidence: "No platform lets human trainers USE AI form analysis to scale 1:many. 300k+ certified trainers in US, each capped at ~30 clients.", size: "LARGE - $1B OPPORTUNITY" }
    ];

    gaps.forEach((g, i) => {
        const y = 1.3 + i * 0.85;
        slide.addText(`${i+1}. ${g.gap}`, { x: 0.5, y: y, w: 9, h: 0.35, fontFace: "Cambria", fontSize: 16, bold: true, color: "F96167" });
        slide.addText(g.evidence, { x: 0.5, y: y + 0.35, w: 7.5, h: 0.45, fontFace: "Calibri", fontSize: 12, color: "2F3C7E" });
        slide.addText(g.size, { x: 8.2, y: y, w: 1.5, h: 0.35, fontFace: "Cambria", fontSize: 12, bold: true, color: g.size === "LARGE - $1B OPPORTUNITY" ? "F96167" : g.size === "LARGE" ? "F9E795" : "065A82", align: "right" });
    });

    slide.addText("The $1B Company: B2B2C Platform for Trainers - Shopify for Personal Trainers with AI Form Analysis as Killer Feature", { x: 0.5, y: 5.0, w: 9, h: 0.5, fontFace: "Calibri", fontSize: 14, bold: true, color: "F96167" });

    // ============================================================
    // SLIDE 8: RECOMMENDED USP
    // ============================================================
    slide = pres.addSlide({ masterName: "CONTENT_SLIDE", sectionTitle: "USP" });
    slide.addText("Recommended Unique Selling Proposition", {
        placeholder: "title",
        fontFace: "Cambria",
        fontSize: 36,
        bold: true,
        color: "2F3C7E"
    });

    slide.addText("The only AI form coach that works on any device, requires zero equipment, and lets your actual human trainer see your reps in real-time - for the price of a coffee.", {
        x: 0.5,
        y: 1.5,
        w: 9,
        h: 1.2,
        fontFace: "Cambria",
        fontSize: 24,
        bold: true,
        color: "F96167",
        align: "center",
        lineSpacing: 1.3
    });

    const uspReasons = [
        { label: "Hard to Copy", detail: "Requires trainer dashboard, client management, video review workflow, payment splitting - not just pose estimation." },
        { label: "High Value", detail: "Solves trainer's scaling problem (income ceiling) + client's accountability problem. Two-sided value." },
        { label: "One Sentence", detail: "Passes the grandmother test. Clear, memorable, shareable." },
        { label: "Long-Term Moat", detail: "Network effects (trainer<->client), data flywheel (labeled reps from pros), switching costs (trainer's business runs on it)." }
    ];

    uspReasons.forEach((u, i) => {
        const y = 3.0 + i * 0.5;
        slide.addText(`${i+1}. ${u.label}`, { x: 1, y: y, w: 2.5, h: 0.4, fontFace: "Cambria", fontSize: 15, bold: true, color: "2F3C7E" });
        slide.addText(u.detail, { x: 3.5, y: y, w: 6, h: 0.4, fontFace: "Calibri", fontSize: 13, color: "2F3C7E" });
    });

    slide.addText("Stronger than competitors: Tempo sells hardware; Zenia sells yoga; Kaia sells rehab; Caliber sells humans. Nobody sells the trainer-tool + client-app loop.", {
        x: 0.5,
        y: 4.9,
        w: 9,
        h: 0.5,
        fontFace: "Calibri",
        fontSize: 13,
        color: "F96167",
        bold: true,
        align: "center"
    });

    // ============================================================
    // SLIDE 9: REVENUE OPPORTUNITIES
    // ============================================================
    slide = pres.addSlide({ masterName: "CONTENT_SLIDE", sectionTitle: "Revenue" });
    slide.addText("Revenue Streams (Ranked by Profitability)", {
        placeholder: "title",
        fontFace: "Cambria",
        fontSize: 36,
        bold: true,
        color: "2F3C7E"
    });

    const revHeaders = ["Rank", "Stream", "Model", "Margin", "Effort", "Notes"];
    const revRows = [
        ["1", "Trainer SaaS (B2B2C)", "$50-100/mo per trainer", "85%", "High", "Core moat; network effects"],
        ["2", "Consumer Pro Sub", "$15-20/mo", "80%", "Medium", "Direct; high churn risk"],
        ["3", "Enterprise/Wellness", "$5-10 PEPM", "75%", "High", "Employers/insurers; long sales cycle"],
        ["4", "White-Label for Gyms", "$500-2k/mo per location", "70%", "High", "Gym chains want branded app"],
        ["5", "Affiliate/Equipment", "5-10% commission", "95%", "Low", "Link to Rogue, Titan, Amazon"],
        ["6", "Premium Exercise Library", "$5/mo add-on", "90%", "Medium", "Video demos, progressions, mobility"],
        ["7", "API Access", "$0.01/analysis", "60%", "High", "Other apps embed form check"],
        ["8", "Data/Analytics (Anon)", "License to researchers", "50%", "Very High", "Ethical/legal minefield"],
        ["9", "Certification/CEU", "$100-300/course", "85%", "Medium", "Trainers need CEUs; you have platform"],
        ["10", "Marketplace (Trainer Finder)", "15-20% take rate", "70%", "Very High", "Chicken-egg; need liquidity first"]
    ];

    const revTableData = [revHeaders, ...revRows];
    slide.addTable(revTableData, {
        x: 0.3,
        y: 1.1,
        w: 9.4,
        h: 4.2,
        fontFace: "Calibri",
        fontSize: 9.5,
        color: "2F3C7E",
        border: { pt: 1, color: "E0E0E0" },
        rowColors: ["2F3C7E", "FFFFFF", "FFF8F8"],
        headerRow: true,
        headerColor: "2F3C7E",
        headerFontColor: "FFFFFF",
        colWidths: [0.4, 1.5, 1.4, 0.7, 0.7, 3.7]
    });

    // ============================================================
    // SLIDE 10: FINANCIAL PROJECTIONS & ASSUMPTIONS
    // ============================================================
    slide = pres.addSlide({ masterName: "CONTENT_SLIDE", sectionTitle: "Financials" });
    slide.addText("Financial Projections & Key Assumptions", {
        placeholder: "title",
        fontFace: "Cambria",
        fontSize: 36,
        bold: true,
        color: "2F3C7E"
    });

    // Assumptions left
    slide.addText("KEY ASSUMPTIONS", { x: 0.5, y: 1.3, w: 4, h: 0.4, fontFace: "Cambria", fontSize: 16, bold: true, color: "F96167" });
    const assumptions = [
        "Starting capital: $50k (founder savings)",
        "Team: 2 founders (eng + product) + 1 ML contractor",
        "Consumer churn: 8%/mo (industry avg); Trainer churn: 3%/mo",
        "CAC: Consumer $45 (content+referral); Trainer $200 (outbound)",
        "LTV: Consumer $180 (15mo @ $12); Trainer $1,800 (36mo @ $50)",
        "Gross margin: 80% (cloud + payment fees only)",
        "Trainer channel = lever (LTV 10x consumer)"
    ];
    assumptions.forEach((a, i) => {
        slide.addText(a, { x: 0.5, y: 1.7 + i * 0.35, w: 4.5, h: 0.35, fontFace: "Calibri", fontSize: 11, color: "2F3C7E", bullet: true, breakLine: true });
    });

    // Projections right
    slide.addText("PROJECTIONS", { x: 5.5, y: 1.3, w: 4, h: 0.4, fontFace: "Cambria", fontSize: 16, bold: true, color: "F96167" });
    const projections = [
        ["Metric", "Value"],
        ["MVP Cost (3 mo)", "$30k"],
        ["Monthly OpEx (Yr 1)", "$8k"],
        ["Break-Even", "Month 14"],
        ["Year 1 Revenue", "$120k"],
        ["Year 3 Revenue", "$1.2M"],
        ["Year 5 Revenue", "$6.5M"],
        ["EBITDA Margin (Yr 5)", "35%"],
        ["", ""],
        ["Sensitivity: Trainer channel fails -> Yr 5 = $2.1M"]
    ];
    const projTableData = projections;
    slide.addTable(projTableData, {
        x: 5.5,
        y: 1.7,
        w: 4,
        h: 3.5,
        fontFace: "Calibri",
        fontSize: 12,
        color: "2F3C7E",
        border: { pt: 1, color: "E0E0E0" },
        rowColors: ["2F3C7E", "FFFFFF", "FFF8F8"],
        headerRow: true,
        headerColor: "2F3C7E",
        headerFontColor: "FFFFFF",
        colWidths: [2.2, 1.8]
    });

    // ============================================================
    // SLIDE 11: GO-TO-MARKET STRATEGY
    // ============================================================
    slide = pres.addSlide({ masterName: "CONTENT_SLIDE", sectionTitle: "GTM" });
    slide.addText("Go-to-Market Strategy (Limited Budget)", {
        placeholder: "title",
        fontFace: "Cambria",
        fontSize: 36,
        bold: true,
        color: "2F3C7E"
    });

    const gtmPhases = [
        { phase: "FIRST 100 USERS", target: "Friends, fitness subreddits, Discord, Twitter", tactics: "Product Hunt launch\nForm Check Friday Twitter threads\nFree 30-day for feedback\nDiscord community for form checks", budget: "$0" },
        { phase: "FIRST 1,000 USERS", target: "Organic search, micro-influencers, trainer referrals", tactics: "SEO: squat form check app, AI personal trainer free\n20 micro-influencers (10-50k) -> free lifetime\nTrainer beta: 10 trainers free 6mo + rev share\nReddit: r/fitness, r/homegym weekly posts", budget: "$2k" },
        { phase: "FIRST 10,000 USERS", target: "Content + referral flywheel + paid test", tactics: "YouTube Shorts/TikTok daily: Is your squat killing knees?\nReferral: 1 free month per referral (both sides)\nTrainer affiliate: $20 per referred trainer\nTest Meta/Google ads at $30 CAC target\nAppSumo/LTD launch for cash + users", budget: "$15k" }
    ];

    gtmPhases.forEach((g, i) => {
        const y = 1.3 + i * 1.35;
        slide.addText(g.phase, { x: 0.5, y: y, w: 2, h: 0.35, fontFace: "Cambria", fontSize: 15, bold: true, color: "F96167" });
        slide.addText(`Target: ${g.target}`, { x: 0.5, y: y + 0.35, w: 3, h: 0.3, fontFace: "Calibri", fontSize: 11, color: "2F3C7E" });
        slide.addText(`Budget: ${g.budget}`, { x: 3.5, y: y + 0.35, w: 2, h: 0.3, fontFace: "Calibri", fontSize: 11, bold: true, color: "065A82" });
        slide.addText(g.tactics, { x: 0.5, y: y + 0.65, w: 5.5, h: 0.6, fontFace: "Calibri", fontSize: 10, color: "2F3C7E" });
    });

    // Organic tactics on right
    slide.addText("ORGANIC GROWTH TACTICS", { x: 6.5, y: 1.3, w: 3, h: 0.4, fontFace: "Cambria", fontSize: 15, bold: true, color: "F96167" });
    const organic = [
        "Form Fix of the Day email (daily, 2-min read)",
        "Public leaderboards (anonymized) for reps/holds",
        "Exportable Form Report Card PDF for social sharing",
        "Trainer content: How I scaled to 100 clients with GYMSENSE",
        "Trainer referral program: $20 per trainer",
        "SEO content clusters: exercise form guides"
    ];
    organic.forEach((o, i) => {
        slide.addText(o, { x: 6.5, y: 1.7 + i * 0.35, w: 3, h: 0.35, fontFace: "Calibri", fontSize: 11, color: "2F3C7E", bullet: true, breakLine: true });
    });

    // ============================================================
    // SLIDE 12: MOAT ANALYSIS
    // ============================================================
    slide = pres.addSlide({ masterName: "CONTENT_SLIDE", sectionTitle: "Moats" });
    slide.addText("Competitive Moat Analysis", {
        placeholder: "title",
        fontFace: "Cambria",
        fontSize: 36,
        bold: true,
        color: "2F3C7E"
    });

    const moatHeaders = ["Moat Type", "Current (B2C)", "With Trainer Platform", "Verdict"];
    const moatRows = [
        ["Network Effects", "None", "STRONG (trainer<->client<->data)", "BUILD THIS"],
        ["Brand", "Zero", "Medium (trainer influencers)", "Long-term"],
        ["Data Advantage", "None", "STRONG (labeled reps + outcomes)", "Core asset"],
        ["AI Advantage", "None (MediaPipe open)", "Medium (fine-tuned on pro data)", "Defensible"],
        ["Switching Costs", "Zero", "HIGH (trainer's roster, billing, programs)", "KEY MOAT"],
        ["Community", "None", "Medium (trainer-led groups)", "Buildable"],
        ["Economies of Scale", "Low", "Medium (cloud costs drop)", "Minor"],
        ["Distribution", "None", "STRONG (trainer = distribution)", "CRITICAL"],
        ["Technology", "Low (commodity CV)", "Medium (real-time multi-person)", "Patentable?"],
        ["IP", "None", "2-3 patents possible", "File early"]
    ];

    const moatTableData = [moatHeaders, ...moatRows];
    slide.addTable(moatTableData, {
        x: 0.3,
        y: 1.1,
        w: 9.4,
        h: 4.2,
        fontFace: "Calibri",
        fontSize: 10,
        color: "2F3C7E",
        border: { pt: 1, color: "E0E0E0" },
        rowColors: ["2F3C7E", "FFFFFF", "FFF8F8"],
        headerRow: true,
        headerColor: "2F3C7E",
        headerFontColor: "FFFFFF",
        colWidths: [1.5, 2, 3.5, 1.4]
    });

    slide.addText("Bottom Line: Without trainer platform = ZERO MOAT. With it = 3 STRONG MOATS (network, switching, distribution).", {
        x: 0.5,
        y: 5.0,
        w: 9,
        h: 0.4,
        fontFace: "Calibri",
        fontSize: 13,
        bold: true,
        color: "F96167",
        align: "center"
    });

    // ============================================================
    // SLIDE 13: TOP 10 RISKS & MITIGATIONS
    // ============================================================
    slide = pres.addSlide({ masterName: "CONTENT_SLIDE", sectionTitle: "Risks" });
    slide.addText("Top 10 Risks & Mitigations", {
        placeholder: "title",
        fontFace: "Cambria",
        fontSize: 36,
        bold: true,
        color: "2F3C7E"
    });

    const riskHeaders = ["#", "Risk", "Likelihood", "Impact", "Mitigation"];
    const riskRows = [
        ["1", "Trainer adoption fails - don't trust AI or won't pay", "High", "Fatal", "10 pilot trainers free; build features they request; revenue share"],
        ["2", "MediaPipe accuracy insufficient - false positives frustrate", "Med", "High", "Confidence threshold UI; user corrections; collect labels for fine-tuning"],
        ["3", "Apple/Google launch native form check (Vision/ML Kit)", "Med", "High", "Differentiate on trainer workflow, not just detection; move fast"],
        ["4", "Camera permission friction kills conversion", "High", "Med", "Progressive onboarding; try without camera mode; PWA install"],
        ["5", "Consumer churn >10%/mo (industry norm)", "High", "Med", "Trainer accountability reduces churn; gamification; contracts"],
        ["6", "Unit economics don't work (CAC > LTV)", "Med", "High", "Focus on trainer channel (LTV $1,800 vs $180); organic only"],
        ["7", "Privacy backlash - app watches me exercise", "Low", "High", "Local processing option; clear policy; no video storage default"],
        ["8", "Competitor copies trainer platform (Tempo, Caliber)", "Med", "High", "Speed; exclusive trainer contracts; data flywheel"],
        ["9", "Injury liability - user hurts self following bad AI advice", "Low", "Fatal", "Disclaimers; not medical advice; insurance; confidence gating"],
        ["10", "Founder burnout / cofounder conflict", "Med", "Fatal", "Vesting; therapy; advisor board; clear decision rights"]
    ];

    const riskTableData = [riskHeaders, ...riskRows];
    slide.addTable(riskTableData, {
        x: 0.3,
        y: 1.0,
        w: 9.4,
        h: 4.4,
        fontFace: "Calibri",
        fontSize: 9,
        color: "2F3C7E",
        border: { pt: 1, color: "E0E0E0" },
        rowColors: ["2F3C7E", "FFFFFF", "FFF8F8"],
        headerRow: true,
        headerColor: "2F3C7E",
        headerFontColor: "FFFFFF",
        colWidths: [0.3, 2.2, 0.7, 0.6, 4.6]
    });

    // ============================================================
    // SLIDE 14: VC PERSPECTIVE
    // ============================================================
    slide = pres.addSlide({ masterName: "CONTENT_SLIDE", sectionTitle: "VC View" });
    slide.addText("VC Perspective (Sequoia / Accel / YC / a16z)", {
        placeholder: "title",
        fontFace: "Cambria",
        fontSize: 36,
        bold: true,
        color: "2F3C7E"
    });

    slide.addText("WOULD WE INVEST TODAY?  ->  NO", {
        x: 0.5,
        y: 1.3,
        w: 9,
        h: 0.5,
        fontFace: "Cambria",
        fontSize: 24,
        bold: true,
        color: "F96167",
        align: "center"
    });

    const redFlags = [
        { flag: "No Distribution Strategy", detail: "Build it and they will come fails in fitness. CAC will be $80+, LTV $150." },
        { flag: "No Moat", detail: "MediaPipe is free. Any dev can clone in 2 weeks. Zero switching costs." },
        { flag: "TAM Inflation", detail: "$140B digital fitness != your market. SAM ~$50M without trainer channel." },
        { flag: "Team Gap", detail: "No fitness domain expert. No trainer relationships. No GTM experience." },
        { flag: "Zero Traction", detail: "0 users, 0 revenue, 0 pilots. Just code." }
    ];

    redFlags.forEach((r, i) => {
        const y = 2.0 + i * 0.6;
        slide.addText(`RED FLAG: ${r.flag}`, { x: 0.5, y: y, w: 2.5, h: 0.35, fontFace: "Cambria", fontSize: 15, bold: true, color: "F96167" });
        slide.addText(r.detail, { x: 3, y: y, w: 6.5, h: 0.35, fontFace: "Calibri", fontSize: 12, color: "2F3C7E" });
    });

    slide.addText("WHAT NEEDS TO CHANGE BEFORE INVESTING:", { x: 0.5, y: 5.0, w: 9, h: 0.4, fontFace: "Cambria", fontSize: 16, bold: true, color: "F96167" });
    const changes = [
        "10 pilot trainers using it with 50+ paying clients, 3-month retention data",
        "Trainer dashboard MVP (client mgmt, program builder, video review, billing)",
        "Pre-seed metrics: $10k MRR, 5% weekly growth, <5% trainer churn",
        "Domain cofounder (ex-trainer or gym owner)"
    ];
    changes.forEach((c, i) => {
        slide.addText(c, { x: 0.5, y: 5.4 + i * 0.35, w: 9, h: 0.35, fontFace: "Calibri", fontSize: 12, color: "2F3C7E", bullet: true, breakLine: true });
    });

    // ============================================================
    // SLIDE 15: PRE-SEED VALUATION
    // ============================================================
    slide = pres.addSlide({ masterName: "CONTENT_SLIDE", sectionTitle: "Valuation" });
    slide.addText("Pre-Seed Valuation Range", {
        placeholder: "title",
        fontFace: "Cambria",
        fontSize: 36,
        bold: true,
        color: "2F3C7E"
    });

    slide.addText("WITH TRAINER TRACTION (above metrics achieved):", { x: 0.5, y: 1.5, w: 9, h: 0.4, fontFace: "Cambria", fontSize: 18, bold: true, color: "F96167" });
    slide.addText("$4M - $7M cap on $500k - $750k raise", { x: 0.5, y: 2.0, w: 9, h: 0.5, fontFace: "Cambria", fontSize: 28, bold: true, color: "2F3C7E", align: "center" });

    slide.addText("WITHOUT TRAINER TRACTION (team + tech bet only):", { x: 0.5, y: 3.0, w: 9, h: 0.4, fontFace: "Cambria", fontSize: 18, bold: true, color: "F9E795" });
    slide.addText("$1.5M - $2.5M cap on $250k raise", { x: 0.5, y: 3.5, w: 9, h: 0.5, fontFace: "Cambria", fontSize: 28, bold: true, color: "2F3C7E", align: "center" });

    slide.addText("Key Insight: The Trainer Platform pivot increases valuation 3-4x by creating defensible moats and 10x LTV.", {
        x: 0.5,
        y: 4.5,
        w: 9,
        h: 0.5,
        fontFace: "Calibri",
        fontSize: 14,
        bold: true,
        color: "F96167",
        align: "center"
    });

    // ============================================================
    // SLIDE 16: FINAL VERDICT
    // ============================================================
    slide = pres.addSlide({ masterName: "CONTENT_SLIDE", sectionTitle: "Verdict" });
    slide.addText("Final Verdict", {
        placeholder: "title",
        fontFace: "Cambria",
        fontSize: 36,
        bold: true,
        color: "2F3C7E"
    });

    const verdictMetrics = [
        { label: "Overall Score", value: "42/100", color: "F96167" },
        { label: "Prob. of Success (> $0)", value: "35%", color: "F9E795" },
        { label: "Prob. of $1M ARR", value: "18%", color: "065A82" },
        { label: "Prob. of $10M ARR", value: "4%", color: "1C7293" },
        { label: "Prob. of Unicorn", value: "0.3%", color: "2F3C7E" }
    ];

    verdictMetrics.forEach((v, i) => {
        slide.addText(v.value, { x: 0.5 + i * 1.85, y: 1.5, w: 1.6, h: 0.8, fontFace: "Cambria", fontSize: 32, bold: true, color: v.color, align: "center" });
        slide.addText(v.label, { x: 0.5 + i * 1.85, y: 2.3, w: 1.6, h: 0.5, fontFace: "Calibri", fontSize: 11, color: "2F3C7E", align: "center" });
    });

    slide.addText("Confidence Level: 80% (based on public comps, fitness app benchmarks, VC patterns)", {
        x: 0.5,
        y: 3.0,
        w: 9,
        h: 0.4,
        fontFace: "Calibri",
        fontSize: 13,
        color: "888888",
        align: "center"
    });

    // ============================================================
    // SLIDE 17: THE 10X IMPROVEMENT (PIVOT)
    // ============================================================
    slide = pres.addSlide({ masterName: "CONTENT_SLIDE", sectionTitle: "Pivot" });
    slide.addText("Single Biggest Improvement: 10x Impact", {
        placeholder: "title",
        fontFace: "Cambria",
        fontSize: 36,
        bold: true,
        color: "2F3C7E"
    });

    slide.addText("PIVOT: B2C AI Trainer App  ->  B2B2C Trainer Operating System with AI Form Analysis", {
        x: 0.5,
        y: 1.4,
        w: 9,
        h: 0.7,
        fontFace: "Cambria",
        fontSize: 20,
        bold: true,
        color: "F96167",
        align: "center",
        lineSpacing: 1.3
    });

    const pivotCompare = [
        { metric: "CAC", current: "$45-80", pivoted: "$200 (but LTV: $1,800)" },
        { metric: "Monthly Churn", current: "8%", pivoted: "3%" },
        { metric: "Moat", current: "None", pivoted: "Network effects + switching costs" },
        { metric: "Competition", current: "Free (Nike, YouTube)", pivoted: "Enabling paid pros (they pay you)" },
        { metric: "Relationship", current: "1:1 user", pivoted: "1:many (trainer brings clients)" },
        { metric: "Price Ceiling", current: "$15/mo", pivoted: "$50-100/mo per trainer + upsell" },
        { metric: "Distribution", current: "None", pivoted: "Trainers = distribution channel" }
    ];

    const pivotHeaders = ["Metric", "Current Path (B2C)", "Pivoted Path (B2B2C)"];
    const pivotRows = pivotCompare.map(p => [p.metric, p.current, p.pivoted]);
    const pivotTableData = [pivotHeaders, ...pivotRows];
    slide.addTable(pivotTableData, {
        x: 0.5,
        y: 2.3,
        w: 9,
        h: 2.5,
        fontFace: "Calibri",
        fontSize: 12,
        color: "2F3C7E",
        border: { pt: 1, color: "E0E0E0" },
        rowColors: ["2F3C7E", "FFFFFF", "FFF8F8"],
        headerRow: true,
        headerColor: "2F3C7E",
        headerFontColor: "FFFFFF",
        colWidths: [1.5, 3.5, 4]
    });

    slide.addText("EXECUTION PLAN FOR PIVOT:", { x: 0.5, y: 4.9, w: 9, h: 0.4, fontFace: "Cambria", fontSize: 16, bold: true, color: "F96167" });
    const execPlan = [
        "Week 1-2: Interview 20 trainers -> What would make you pay $50/mo?",
        "Week 3-6: Build trainer dashboard (client list, session view, programs, billing)",
        "Week 7-10: Pilot with 5 trainers, 25 clients -> measure time saved, retention, accuracy",
        "Week 11-12: Iterate -> launch paid beta at $29/mo (grandfather price)",
        "Month 4: Raise pre-seed on TRACTION, not code"
    ];
    execPlan.forEach((e, i) => {
        slide.addText(e, { x: 0.5, y: 5.3 + i * 0.3, w: 9, h: 0.3, fontFace: "Calibri", fontSize: 11, color: "2F3C7E", bullet: true, breakLine: true });
    });

    // ============================================================
    // SLIDE 18: CLOSING / CONTACT
    // ============================================================
    slide = pres.addSlide({ masterName: "TITLE_SLIDE" });
    slide.addText("GYMSENSE", {
        placeholder: "title",
        fontFace: "Cambria",
        fontSize: 48,
        bold: true,
        color: "FFFFFF",
        align: "center"
    });
    slide.addText("AI Form Coach -> Trainer Operating System\n\nReady to build the platform that scales human expertise.\n\nLet's talk.", {
        placeholder: "body",
        fontFace: "Calibri",
        fontSize: 22,
        color: "F9E795",
        align: "center"
    });
    slide.addText("Founder: [Your Name]  |  Email: [your@email.com]  |  GitHub: github.com/yourusername/gymsense", {
        x: 1,
        y: 4.8,
        w: 8,
        h: 0.5,
        fontFace: "Calibri",
        fontSize: 14,
        color: "F96167",
        align: "center"
    });

    // ============================================================
    // WRITE FILE
    // ============================================================
    const outputPath = "C:/Users/HP/Desktop/GYMSENSE/GYMSENSE_Startup_Bihar_PitchDeck.pptx";
    await pres.writeFile({ fileName: outputPath });
    console.log("Pitch deck saved to:", outputPath);
}

createDeck().catch(console.error);