Multimodal Agentic AI for Aircraft Structural Defect Assessment and Maintenance Decision Support

That is a solid M.Tech-level direction because it combines:

Computer Vision for defect understanding,
NLP for techlog/manual/history understanding,
Conversational AI for engineer interaction,
Agentic orchestration for multi-step reasoning and tool use,
ML system optimization for deployment and latency,
and it stays aligned to airline eTechLog / maintenance workflows. IATA’s electronic logbook roadmap specifically highlights pain around manual interpretation, missing data, and workflow inefficiency, while EASA’s AI guidance emphasizes assistive, traceable, human-supervised AI—exactly the kind of framing you want.
What makes it better than “just image defect detection”

A plain CV project like “classify crack/scratch from image” is usually too narrow. A stronger dissertation is one where the system:

analyzes the image,
reads the related techlog entry,
retrieves relevant manual / MEL / prior cases,
reasons over all of that,
proposes an action or ranked options,
asks for human confirmation,
logs the decision trail.

That fits the current strengths of retrieval-augmented generation, multimodal learning, and aviation AI governance much better than a standalone classifier.

Best dissertation angle

I would shape it like this:

Recommended title

Agentic Multimodal AI Copilot for Aircraft Structural Defect Assessment using Image Analysis, Techlog Context, and Retrieval-Augmented Maintenance Reasoning

That title is strong because it signals:

novelty,
industry relevance,
multiple course areas,
and clear scope.
Core system idea

Your system can have 4 agents:

1. Vision Agent

Takes uploaded inspection image and detects:

crack / dent / corrosion / surface damage,
location,
severity estimate,
confidence score.

You can use modern segmentation/detection approaches rather than only a basic CNN. Foundation-style segmentation models like SAM changed the practicality of image labeling and inspection workflows.

2. Context Agent

Reads:

techlog defect description,
aircraft/tail metadata,
prior similar defects,
ATA chapter / subsystem,
station/environment info.

This turns raw visual detection into operationally meaningful context.

3. Knowledge/RAG Agent

Retrieves:

maintenance manual snippets,
prior resolved cases,
structural repair guidance,
engineering recommendations,
safety constraints.

RAG is important because it grounds outputs in evidence instead of relying only on model memory.

4. Decision/Conversation Agent

Explains:

what defect is likely present,
what evidence supports it,
what actions are possible,
when to escalate to engineering,
what it is unsure about.

This should stay assistive, not autonomous final authority, which aligns better with EASA’s Level 1/2 machine-learning guidance and human oversight expectations.

Where the “agentic AI” part comes in

Do not pitch “agentic AI” as hype. Pitch it as structured orchestration.

Your agentic workflow can be:

Image uploaded → Vision Agent detects defect → Context Agent enriches case → RAG Agent fetches evidence → Decision Agent produces recommendation → Human engineer approves/rejects

That is agentic because the system uses multiple specialized components and tools in sequence, with routing and reasoning. It is also safer and more defendable academically than claiming a fully autonomous maintenance agent.

Novelty options

To make it dissertation-worthy, pick one main novelty and one secondary novelty.

Best main novelty options

Option A — Multimodal fusion
Fuse:

image embeddings,
techlog text embeddings,
historical defect metadata.

Research question:

Does multimodal fusion improve defect severity classification or recommendation quality versus image-only models?

This is the safest and strongest novelty.

Option B — Evidence-grounded maintenance reasoning
The novelty is not only detection, but that the system gives:

cited evidence,
ranked actions,
abstention when uncertain.

That is very practical and aligns with trust/safety requirements.

Option C — Offline/edge-capable agent
Because aviation workflows often involve constrained or semi-offline environments, you can optimize:

compact vision model,
local inference,
delayed sync,
low latency.

That ties well into ML system optimization and your enterprise app background. IATA’s eTechLog guidance explicitly calls out operational realities like workflow controls, device usage, and rollout constraints.

Strong dissertation version I recommend
Final topic recommendation

An Agentic Multimodal AI Copilot for Aircraft Structural Defect Assessment and Maintenance Recommendation using Vision, Techlog NLP, and Retrieval-Augmented Reasoning

Example research questions
Does multimodal fusion outperform image-only defect classification?
Does retrieval-grounded reasoning reduce hallucinated recommendations versus a plain multimodal LLM?
Can an agent-based pipeline improve engineer trust and task completion time compared with a non-agent dashboard?
What is the best tradeoff between latency and accuracy for deployment in maintenance workflows?
Example architecture
Input
inspection images,
techlog text,
metadata,
prior maintenance records.
Pipeline
Vision model → defect type + severity + region
Text/NLP model → extract key terms from techlog
Vector retrieval → fetch prior cases/manual evidence
Agent orchestrator → combine outputs
LLM decision layer → produce explanation and recommendations
Human-in-the-loop UI → approve, reject, comment
Deliverable

A working prototype where an engineer can:

upload a defect image,
see detected region and severity,
get related prior cases/manual references,
chat with the system,
receive evidence-backed recommendations.

That is a very strong demo.

Feasibility check

This is worth trying if you scope it correctly.

Feasible scope
2–4 defect categories only,
one aircraft structural use case,
prototype-level agentic orchestration,
public/synthetic data plus a small private sample if available.
Risky scope
full aircraft structural diagnosis,
too many defect types,
full autonomous decision-making,
huge private dataset dependency.
Best research area dropdown for this topic

Still choose Artificial Intelligence.

Because this topic spans vision, NLP, conversational AI, retrieval, and agent orchestration better than a narrower label like Machine Learning. Your dissertation guide also emphasizes non-trivial, original, application-oriented work aligned with your organization, which this clearly satisfies.



OTHER DETAILS TO BE INCLUDED AS WELL

Topic T1: Safety-grounded RAG Techlog Copilot for defect triage, troubleshooting, and deferral support Novelty. Build a provable-evidence conversational assistant that answers techlog questions by retrieving and citing authoritative artifacts (MEL/CDL extracts, manuals, engineering orders, prior similar techlogs, FAA/EASA advisories), with explicit “abstain / escalate” logic and audit logging aligned to aviation AI guidance.  Research questions / hypotheses.H1: RAG with structured retrieval + safety guardrails reduces hallucination rate and increases task success compared to parametric-only LLM baselines in maintenance QA. H2: Domain adaptation via parameter-efficient fine-tuning (LoRA/QLoRA) improves defect-code classification and “next best action” suggestion accuracy without requiring full-model retraining.  Proposed methods.Model: instruction-following LLM adapted with LoRA/QLoRA; RAG retriever + reranker; tool-form outputs (JSON) for triage actions; safety policy layer (refuse/abstain) and confidence gating. System optimization: vLLM or TensorRT-LLM for low-latency serving; caching for repeated queries; audit-event storage.  Training data needs.Minimum viable (public): FAA SDR + FAA AD text + IATA ELB/AHM documents + curated manuals/handbooks where licensed; construct synthetic QA pairs with SME review. Airline uplift: internal techlog entries + resolutions; MEL/CDL policies; engineering orders. Evaluation metrics.Task success rate (SME graded), citation correctness rate, hallucination rate, abstention precision/recall, defect classification F1, retrieval Recall@k / nDCG, latency (p95), and audit completeness (events logged per query).  Expected deliverables.Evidence-grounded chat prototype integrated into a techlog-like UI; benchmark suite of maintenance QA tasks; safety taxonomy (“can answer / must cite / must abstain”); deployment/runbook and risk assessment aligned to EASA trustworthiness concepts.  Estimated effort/complexity. Medium (high engineering integration, manageable ML). Required resources. 1–2 GPUs for fine-tuning and embedding; vector DB; SME time for ~200–500 QA evaluations; secure document access controls.  Potential industry impact. Faster triage, fewer interpretation errors, better knowledge reuse, and improved traceability (evidence and logs), aligned with regulatory trajectories requiring oversight and record-keeping.  Topic T2: Multimodal Early Warning System for recurring defects using techlog text + ACARS/health signals Novelty. Fuse unstructured defect narratives with telemetry/event streams to detect emerging recurrent defect patterns earlier than current rule-based monitoring, and generate “lead indicator” alerts with interpretable supporting evidence.  Research questions / hypotheses.H1: Joint text–time-series representations outperform text-only models for predicting recurrence within a fixed horizon (e.g., 7/30/90 days). H2: Self-supervised pretraining (contrastive / masked modeling) reduces labeled-data requirements for tail-specific recurring defect prediction.  Proposed methods.Text: transformer encoder fine-tuned on defect taxonomy classification; abbreviation expansion and domain tokenizer. Time-series: event transformer or temporal model over ACARS/health events; late fusion or cross-attention multimodal transformer; uncertainty calibration to support “alert thresholds.” Conversational layer: generate “why this alert” explanation with retrieved similar historical cases (mini-RAG).  Training data needs.Minimum viable: simulate “ACARS-like events” via open prognostics datasets (C-MAPSS) + synthetic mapping to defect categories; techlog-like text via FAA SDR narratives/fields when available. Airline uplift: real ACARS/health messages + techlog entries with recurrence labels (repeat defects, repeated deferrals). Evaluation metrics.Prediction: AUROC/AUPRC, recall at fixed false-alert rate, time-to-detection gain vs baseline, calibration (ECE/Brier), and operational KPI proxy metrics (prevented repeats, estimated delay-risk reduction).  Expected deliverables.Multimodal dataset schema + preprocessing pipeline; trained multimodal model; alert dashboard prototype; ablation studies (text-only vs telemetry-only vs fused); “explainable alert packets” for MCC workflows.  Estimated effort/complexity. Medium–High (depends on telemetry access; strong research content). Required resources. 1–2 GPUs; time-series store; SME validation of alert usefulness; moderate annotation (recurrence labels from history).  Potential industry impact. Earlier intervention on emerging recurrent defects, aligning to IATA’s emphasis on proactive AHM and reducing unpredictable events.  Topic T3: Offline / Safe Deep Reinforcement Learning for maintenance deferral and dispatch reliability under constraints Novelty. Formulate techlog-driven maintenance deferral as a constrained sequential decision problem and learn policies from historical decision traces (offline RL), emphasizing safety constraints, auditability, and counterfactual evaluation rather than live exploration.  Research questions / hypotheses.H1: Offline RL policies can outperform heuristic deferral rules on simulated or historical replay metrics while respecting hard constraints (MEL/CDL-like). H2: Sequence-model RL (Decision Transformer style) reduces sensitivity to reward shaping and supports “what-if” scenario evaluation for maintenance control centers.  Proposed methods.Environment: build a simulator (tail-day timeline) with stochastic defect arrivals; actions = defer/clear/swap aircraft/route; constraints = allowable deferrals and resource capacity; reward = dispatch reliability proxy – delay/cancellation cost. Model: Decision Transformer baseline + constrained policy layer (rule-based shield or penalty methods); offline policy evaluation and stress testing.  Training data needs.Minimum viable: synthetic environment calibrated using IATA cost figures and public reliability assumptions + FAA SDR frequencies as priors. Airline uplift: historical deferral decisions, delay outcomes, and resource constraints. Evaluation metrics.Cumulative reward under constraints; constraint violation rate (must be ~0); simulated delay minutes avoided; robustness across stress scenarios; interpretability of policy decisions (feature attribution / rule traces).  Expected deliverables.Simulator + offline RL training framework; benchmark suite; policy comparison vs heuristics; “human-readable policy explanation” module; governance documentation aligned with EASA trustworthiness and EU logging expectations.  Estimated effort/complexity. High (strong research depth; careful simulation and evaluation required). Required resources. Modest GPU/CPU; main cost is design of realistic simulator and SME review to validate constraints and reward realism.  Potential industry impact. High: deferral decisions directly affect dispatch reliability and delay/cancellation costs highlighted by IATA; even small improvements can be economically significant.  Topic T4: Fleet-wide recurring defect graphs using GNNs over component networks + texts Novelty. Build a heterogeneous graph (tail ↔ component ↔ defect ↔ station ↔ maintenance action) and use graph neural nets to predict “next recurrence hotspots,” combining structured logs and unstructured narratives.  Methods.Graph construction; text embeddings as node features; temporal GNN or dynamic graph modeling; explainable subgraph retrieval for maintainers.  Data.Requires moderate structured history; can prototype with FAA SDR plus synthetic tail mapping. Include these also for the project and give a unified title for dissertation project as i need to submit title