import { useState, useEffect, useRef } from "react";
import { Lock, Shield, ShieldAlert, ShieldCheck, CreditCard, LogOut, Smartphone, Monitor, MapPin, AlertTriangle, CheckCircle2, XCircle, Send } from "lucide-react";

const API_URL = "http://localhost:8000";

// ───────────────────────────────────────────────────────────
// Carte/profil utilisé pour la démo — correspond à un vrai profil
// du dataset (voir profils_utilisateurs.pkl, card1=1009)
// ───────────────────────────────────────────────────────────
const USER_PROFILE = {
  card1: 1009,
  name: "Alinne Hoblos",
  iban: "FR76 3000 4008 2800 0123 4567 890",
  device: "desktop",
  deviceInfo: "Windows",
  os: "Windows 10",
  browser: "chrome 63",
  location: "Paris, France",
};

function classNames(...c) {
  return c.filter(Boolean).join(" ");
}

// ───────────────────────────────────────────────────────────
// ÉCRAN LOGIN
// ───────────────────────────────────────────────────────────
function LoginScreen({ onLogin, apiStatus }) {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("agent2026");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      if (!res.ok) throw new Error("Identifiants incorrects");
      const data = await res.json();
      onLogin(data.access_token);
    } catch (err) {
      setError(
        apiStatus === "offline"
          ? "Impossible de contacter l'API. Vérifiez qu'elle tourne sur localhost:8000."
          : "Identifiants incorrects. Réessayez."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-[#0B1E3D] relative overflow-hidden">
      {/* texture de fond subtile */}
      <div
        className="absolute inset-0 opacity-[0.04]"
        style={{
          backgroundImage:
            "radial-gradient(circle at 1px 1px, white 1px, transparent 0)",
          backgroundSize: "32px 32px",
        }}
      />
      <div className="relative z-10 w-full max-w-sm px-6">
        <div className="flex flex-col items-center mb-8">
          <div className="w-14 h-14 rounded-2xl bg-[#C9A24B] flex items-center justify-center mb-4 shadow-lg shadow-[#C9A24B]/20">
            <Lock className="w-7 h-7 text-[#0B1E3D]" strokeWidth={2.2} />
          </div>
          <h1 className="text-[#F4F1EA] text-xl font-semibold tracking-tight">
            Meridian Banque
          </h1>
          <p className="text-[#8DA3C7] text-sm mt-1">
            Authentification continue activée
          </p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="bg-[#10274D] border border-[#1E3A66] rounded-2xl p-6 shadow-2xl"
        >
          <div className="mb-4">
            <label className="block text-xs font-medium text-[#8DA3C7] mb-1.5 tracking-wide uppercase">
              Identifiant
            </label>
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-[#0B1E3D] border border-[#1E3A66] rounded-lg px-3 py-2.5 text-[#F4F1EA] text-sm focus:outline-none focus:ring-2 focus:ring-[#C9A24B] focus:border-transparent transition"
              autoComplete="username"
            />
          </div>
          <div className="mb-5">
            <label className="block text-xs font-medium text-[#8DA3C7] mb-1.5 tracking-wide uppercase">
              Mot de passe
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-[#0B1E3D] border border-[#1E3A66] rounded-lg px-3 py-2.5 text-[#F4F1EA] text-sm focus:outline-none focus:ring-2 focus:ring-[#C9A24B] focus:border-transparent transition"
              autoComplete="current-password"
            />
          </div>

          {error && (
            <div className="mb-4 text-xs text-[#E08585] bg-[#3A1414] border border-[#5C1F1F] rounded-lg px-3 py-2">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-[#C9A24B] hover:bg-[#D9B45F] disabled:opacity-60 text-[#0B1E3D] font-semibold text-sm rounded-lg py-2.5 transition"
          >
            {loading ? "Connexion..." : "Se connecter"}
          </button>

          <div className="flex items-center justify-center gap-1.5 mt-4 text-[11px]">
            <span
              className={classNames(
                "w-1.5 h-1.5 rounded-full",
                apiStatus === "online" ? "bg-emerald-400" : "bg-red-400"
              )}
            />
            <span className="text-[#5E7AA8]">
              API {apiStatus === "online" ? "connectée" : "hors ligne"} — localhost:8000
            </span>
          </div>
        </form>

        <p className="text-center text-[#46618F] text-xs mt-6">
          Agent IA d'authentification continue · démonstration TER
        </p>
      </div>
    </div>
  );
}

// ───────────────────────────────────────────────────────────
// BADGE NIVEAU
// ───────────────────────────────────────────────────────────
function NiveauBadge({ niveau }) {
  const map = {
    VERT: { bg: "bg-emerald-500/15", text: "text-emerald-400", border: "border-emerald-500/30", icon: ShieldCheck, label: "Accès accordé" },
    ORANGE: { bg: "bg-amber-500/15", text: "text-amber-400", border: "border-amber-500/30", icon: Shield, label: "Vérification requise" },
    ROUGE: { bg: "bg-red-500/15", text: "text-red-400", border: "border-red-500/30", icon: ShieldAlert, label: "Accès bloqué" },
  };
  const cfg = map[niveau] || map.VERT;
  const Icon = cfg.icon;
  return (
    <span
      className={classNames(
        "inline-flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full border",
        cfg.bg,
        cfg.text,
        cfg.border
      )}
    >
      <Icon className="w-3.5 h-3.5" />
      {cfg.label}
    </span>
  );
}

// ───────────────────────────────────────────────────────────
// MODAL OTP
// ───────────────────────────────────────────────────────────
function OtpModal({ onSubmit, onCancel, scenario, expiresIn = 90, sending, error }) {
  const [code, setCode] = useState(["", "", "", "", "", ""]);
  const [timeLeft, setTimeLeft] = useState(expiresIn);
  const [submitting, setSubmitting] = useState(false);
  const refs = useRef([]);

  useEffect(() => {
    if (timeLeft <= 0) return;
    const t = setTimeout(() => setTimeLeft((s) => s - 1), 1000);
    return () => clearTimeout(t);
  }, [timeLeft]);

  function handleChange(i, val) {
    if (!/^[0-9]?$/.test(val)) return;
    const next = [...code];
    next[i] = val;
    setCode(next);
    if (val && i < 5) refs.current[i + 1]?.focus();
  }

  function handleKeyDown(i, e) {
    if (e.key === "Backspace" && !code[i] && i > 0) {
      refs.current[i - 1]?.focus();
    }
  }

  const full = code.every((c) => c !== "");

  async function submit() {
    setSubmitting(true);
    await onSubmit(code.join(""));
    setSubmitting(false);
  }

  const minutes = Math.floor(timeLeft / 60);
  const seconds = timeLeft % 60;

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 px-4">
      <div className="bg-[#10274D] border border-[#1E3A66] rounded-2xl p-6 max-w-sm w-full shadow-2xl">
        <div className="flex items-center gap-2 mb-1">
          <Send className="w-5 h-5 text-amber-400" />
          <h3 className="text-[#F4F1EA] font-semibold text-base">
            Vérification de sécurité
          </h3>
        </div>
        <p className="text-[#8DA3C7] text-sm mb-4">
          {sending
            ? "Envoi du code en cours..."
            : scenario === "device"
            ? "Connexion détectée depuis un nouvel appareil. Un code à 6 chiffres a été envoyé à votre adresse email."
            : "Activité inhabituelle détectée. Saisissez le code reçu par email pour confirmer votre identité."}
        </p>

        <div className="flex gap-2 justify-center mb-4">
          {code.map((c, i) => (
            <input
              key={i}
              ref={(el) => (refs.current[i] = el)}
              value={c}
              onChange={(e) => handleChange(i, e.target.value)}
              onKeyDown={(e) => handleKeyDown(i, e)}
              maxLength={1}
              disabled={sending}
              className="w-10 h-12 text-center text-lg font-semibold bg-[#0B1E3D] border border-[#1E3A66] rounded-lg text-[#F4F1EA] focus:outline-none focus:ring-2 focus:ring-[#C9A24B] disabled:opacity-40"
            />
          ))}
        </div>

        {error && (
          <p className="text-center text-xs text-red-400 mb-3">{error}</p>
        )}

        <p className="text-center text-xs text-[#5E7AA8] mb-4">
          {sending ? (
            "Patientez..."
          ) : timeLeft > 0 ? (
            <>Code valide encore <span className="text-amber-400 font-medium">{minutes}:{String(seconds).padStart(2, "0")}</span></>
          ) : (
            <span className="text-red-400">Code expiré — relancez la vérification</span>
          )}
        </p>

        <div className="flex gap-2">
          <button
            onClick={onCancel}
            className="flex-1 bg-transparent border border-[#1E3A66] text-[#8DA3C7] text-sm font-medium rounded-lg py-2.5 hover:bg-[#1E3A66] transition"
          >
            Annuler
          </button>
          <button
            onClick={submit}
            disabled={!full || timeLeft <= 0 || sending || submitting}
            className="flex-1 bg-[#C9A24B] hover:bg-[#D9B45F] disabled:opacity-40 text-[#0B1E3D] text-sm font-semibold rounded-lg py-2.5 transition"
          >
            {submitting ? "Vérification..." : "Confirmer"}
          </button>
        </div>
      </div>
    </div>
  );
}

// ───────────────────────────────────────────────────────────
// TOAST RESULTAT
// ───────────────────────────────────────────────────────────
function ResultToast({ result, onClose }) {
  if (!result) return null;
  const isBlocked = result.niveau === "ROUGE";
  const isOrange = result.niveau === "ORANGE";

  const cfg = isBlocked
    ? { Icon: XCircle, color: "text-red-400", bg: "bg-[#2A1414]", border: "border-red-500/30" }
    : isOrange
    ? { Icon: AlertTriangle, color: "text-amber-400", bg: "bg-[#2A2014]", border: "border-amber-500/30" }
    : { Icon: CheckCircle2, color: "text-emerald-400", bg: "bg-[#142A20]", border: "border-emerald-500/30" };

  const { Icon } = cfg;

  return (
    <div className="fixed bottom-6 right-6 z-50 max-w-sm animate-[fadeIn_0.2s_ease]">
      <div className={classNames("rounded-xl border p-4 shadow-2xl", cfg.bg, cfg.border)}>
        <div className="flex items-start gap-3">
          <Icon className={classNames("w-5 h-5 mt-0.5 flex-shrink-0", cfg.color)} />
          <div className="flex-1">
            <p className={classNames("text-sm font-semibold", cfg.color)}>
              {isBlocked ? "Session bloquée" : isOrange ? "Vérification requise" : "Transaction validée"}
            </p>
            <p className="text-[#B8C5DC] text-xs mt-1">{result.action}</p>
            <div className="flex gap-3 mt-2 text-[11px] text-[#5E7AA8]">
              <span>Score : {result.score_final?.toFixed(2)}</span>
              {result.location && <span>📍 {result.location}</span>}
            </div>
          </div>
          <button onClick={onClose} className="text-[#5E7AA8] hover:text-[#8DA3C7]">
            <XCircle className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

// ───────────────────────────────────────────────────────────
// DASHBOARD BANCAIRE
// ───────────────────────────────────────────────────────────
function BankDashboard({ token, onLogout }) {
  const [blocked, setBlocked] = useState(false);
  const [result, setResult] = useState(null);
  const [otpScenario, setOtpScenario] = useState(null); // null | "device" | "manual"
  const [pendingTx, setPendingTx] = useState(null);
  const [otpSending, setOtpSending] = useState(false);
  const [otpError, setOtpError] = useState("");
  const [history, setHistory] = useState([
    { id: 1, label: "Café Lutetia", amount: -4.5, date: "Aujourd'hui, 09:12" },
    { id: 2, label: "Virement reçu — Salaire", amount: 2400.0, date: "Hier, 08:00" },
    { id: 3, label: "Loyer appartement", amount: -780.0, date: "01 juin" },
  ]);
  const [loadingAction, setLoadingAction] = useState(null);

  const headers = { "Content-Type": "application/json", Authorization: `Bearer ${token}` };

  async function callAnalyze(payload, label, amount) {
    try {
      const res = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        headers,
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      setResult(data);

      if (data.niveau === "ROUGE") {
        setBlocked(true);
      } else if (data.niveau === "ORANGE") {
        setPendingTx({ label, amount, payload });
        setOtpScenario(payload.DeviceType !== USER_PROFILE.device ? "device" : "manual");
        // Déclenche le vrai envoi d'email via l'API
        setOtpSending(true);
        setOtpError("");
        try {
          await fetch(`${API_URL}/send_otp`, {
            method: "POST",
            headers,
            body: JSON.stringify({ card1: payload.card1 }),
          });
        } catch (e) {
          setOtpError("Échec de l'envoi de l'email. Vérifiez la configuration Gmail SMTP.");
        } finally {
          setOtpSending(false);
        }
      } else {
        setHistory((h) => [{ id: Date.now(), label, amount, date: "À l'instant" }, ...h]);
      }
    } catch (e) {
      setResult({ niveau: "ERREUR", action: "Impossible de contacter l'API. Vérifiez qu'elle tourne." });
    } finally {
      setLoadingAction(null);
    }
  }

  function handleNormalTransaction() {
    setLoadingAction("normal");
    callAnalyze(
      {
        card1: USER_PROFILE.card1,
        DeviceType: USER_PROFILE.device,
        DeviceInfo: USER_PROFILE.deviceInfo,
        id_30: USER_PROFILE.os,
        id_31: USER_PROFILE.browser,
        TransactionAmt: 45.0,
        TransactionDT: 50000,
        location: USER_PROFILE.location,
      },
      "Achat — Fnac.com",
      -45.0
    );
  }

  function handleNewDevice() {
    setLoadingAction("device");
    callAnalyze(
      {
        card1: USER_PROFILE.card1,
        DeviceType: "mobile",
        DeviceInfo: "iPhone 14",
        id_30: "iOS 17",
        id_31: "safari mobile",
        TransactionAmt: 120.0,
        TransactionDT: 50000,
        location: "Lyon, France",
      },
      "Achat — Decathlon",
      -120.0
    );
  }

  function handleAttack() {
    setLoadingAction("attack");
    callAnalyze(
      {
        card1: USER_PROFILE.card1,
        DeviceType: "mobile",
        DeviceInfo: "unknown_device",
        id_30: "Android 9.0",
        id_31: "unknown_browser",
        TransactionAmt: 1950.0,
        TransactionDT: 10800,
        location: "Moscou, Russie",
      },
      "Achat suspect — Moscou",
      -1950.0
    );
  }

  async function handleOtpSubmit(code) {
    setOtpError("");
    try {
      const res = await fetch(`${API_URL}/verify_otp`, {
        method: "POST",
        headers,
        body: JSON.stringify({ card1: pendingTx?.payload?.card1, code }),
      });
      if (!res.ok) {
        const err = await res.json();
        setOtpError(err.detail || "Code incorrect");
        return;
      }
      // Code valide
      setOtpScenario(null);
      if (pendingTx) {
        setHistory((h) => [
          { id: Date.now(), label: pendingTx.label, amount: pendingTx.amount, date: "À l'instant" },
          ...h,
        ]);
      }
      setResult({ niveau: "VERT", action: "Identité confirmée — transaction validée après vérification OTP." });
      setPendingTx(null);
    } catch (e) {
      setOtpError("Impossible de vérifier le code. Vérifiez la connexion à l'API.");
    }
  }

  async function handleUnblock() {
    setLoadingAction("unblock");
    try {
      await fetch(`${API_URL}/unblock/${USER_PROFILE.card1}`, { method: "POST", headers });
      setBlocked(false);
      setResult(null);
    } catch (e) {
      // ignore
    } finally {
      setLoadingAction(null);
    }
  }

  const balance = 3240.75 + history.reduce((s, h) => s + (h.id > 3 ? h.amount : 0), 0);

  if (blocked) {
    return (
      <div className="min-h-screen bg-[#0B1E3D] flex items-center justify-center px-4">
        <div className="max-w-md w-full text-center">
          <div className="w-16 h-16 rounded-full bg-red-500/15 border border-red-500/30 flex items-center justify-center mx-auto mb-5">
            <ShieldAlert className="w-8 h-8 text-red-400" />
          </div>
          <h2 className="text-[#F4F1EA] text-xl font-semibold mb-2">
            Session bloquée pour votre sécurité
          </h2>
          <p className="text-[#8DA3C7] text-sm mb-1">
            Une activité inhabituelle a été détectée sur votre compte :
          </p>
          <p className="text-red-400 text-sm font-medium mb-6">
            {result?.location && `Connexion depuis ${result.location}`} · montant inhabituel
          </p>
          <div className="bg-[#10274D] border border-[#1E3A66] rounded-xl p-4 text-left mb-6 text-xs text-[#8DA3C7] space-y-1.5">
            <div className="flex justify-between"><span>Score de confiance</span><span className="text-red-400 font-medium">{result?.score_final?.toFixed(2)}</span></div>
            <div className="flex justify-between"><span>Action système</span><span className="text-[#F4F1EA]">{result?.action}</span></div>
          </div>
          <button
            onClick={handleUnblock}
            disabled={loadingAction === "unblock"}
            className="w-full bg-[#C9A24B] hover:bg-[#D9B45F] disabled:opacity-60 text-[#0B1E3D] font-semibold text-sm rounded-lg py-3 transition"
          >
            {loadingAction === "unblock" ? "Déblocage..." : "Vérifier mon identité et débloquer"}
          </button>
          <button
            onClick={onLogout}
            className="w-full text-[#5E7AA8] text-xs mt-4 hover:text-[#8DA3C7]"
          >
            Se déconnecter
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F4F1EA]">
      {/* Header */}
      <header className="bg-[#0B1E3D] px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-[#C9A24B] flex items-center justify-center">
            <Lock className="w-4 h-4 text-[#0B1E3D]" />
          </div>
          <span className="text-[#F4F1EA] font-semibold text-sm">Meridian Banque</span>
        </div>
        <button onClick={onLogout} className="flex items-center gap-1.5 text-[#8DA3C7] text-xs hover:text-[#F4F1EA] transition">
          <LogOut className="w-3.5 h-3.5" />
          Déconnexion
        </button>
      </header>

      <main className="max-w-2xl mx-auto px-5 py-8">
        {/* Carte / solde */}
        <div className="bg-[#0B1E3D] rounded-2xl p-6 text-[#F4F1EA] relative overflow-hidden mb-6">
          <div className="absolute -right-8 -top-8 w-40 h-40 rounded-full bg-[#C9A24B]/10" />
          <div className="relative z-10">
            <p className="text-[#8DA3C7] text-xs mb-1">Solde disponible</p>
            <p className="text-3xl font-semibold tracking-tight mb-4">
              {balance.toLocaleString("fr-FR", { minimumFractionDigits: 2 })} €
            </p>
            <div className="flex items-center justify-between text-xs text-[#8DA3C7]">
              <span>{USER_PROFILE.name}</span>
              <span className="flex items-center gap-1.5">
                <CreditCard className="w-3.5 h-3.5" />
                •••• {String(USER_PROFILE.card1).slice(-4)}
              </span>
            </div>
          </div>
        </div>

        {/* Statut agent */}
        <div className="flex items-center gap-2 mb-6 px-1">
          <ShieldCheck className="w-4 h-4 text-emerald-600" />
          <p className="text-xs text-[#5C5648]">
            Surveillance continue active — votre comportement est analysé à chaque transaction
          </p>
        </div>

        {/* Scénarios de démo */}
        <div className="mb-6">
          <p className="text-[11px] font-semibold text-[#8B8470] uppercase tracking-wide mb-3">
            Simuler une transaction
          </p>
          <div className="grid grid-cols-1 gap-3">
            <button
              onClick={handleNormalTransaction}
              disabled={loadingAction !== null}
              className="flex items-center gap-3 bg-white border border-[#E5DFC9] rounded-xl p-4 text-left hover:border-[#C9A24B] transition disabled:opacity-50"
            >
              <div className="w-10 h-10 rounded-full bg-emerald-50 flex items-center justify-center flex-shrink-0">
                <Monitor className="w-5 h-5 text-emerald-600" />
              </div>
              <div className="flex-1">
                <p className="text-[#1A2238] text-sm font-medium">Achat habituel — même appareil</p>
                <p className="text-[#8B8470] text-xs">Fnac.com · 45,00 € · Paris, depuis votre ordinateur</p>
              </div>
              {loadingAction === "normal" && <span className="text-xs text-[#8B8470]">...</span>}
            </button>

            <button
              onClick={handleNewDevice}
              disabled={loadingAction !== null}
              className="flex items-center gap-3 bg-white border border-[#E5DFC9] rounded-xl p-4 text-left hover:border-[#C9A24B] transition disabled:opacity-50"
            >
              <div className="w-10 h-10 rounded-full bg-amber-50 flex items-center justify-center flex-shrink-0">
                <Smartphone className="w-5 h-5 text-amber-600" />
              </div>
              <div className="flex-1">
                <p className="text-[#1A2238] text-sm font-medium">Achat depuis un nouvel appareil</p>
                <p className="text-[#8B8470] text-xs">Decathlon · 120,00 € · Lyon, depuis un iPhone non reconnu</p>
              </div>
              {loadingAction === "device" && <span className="text-xs text-[#8B8470]">...</span>}
            </button>

            <button
              onClick={handleAttack}
              disabled={loadingAction !== null}
              className="flex items-center gap-3 bg-white border border-[#E5DFC9] rounded-xl p-4 text-left hover:border-red-300 transition disabled:opacity-50"
            >
              <div className="w-10 h-10 rounded-full bg-red-50 flex items-center justify-center flex-shrink-0">
                <MapPin className="w-5 h-5 text-red-500" />
              </div>
              <div className="flex-1">
                <p className="text-[#1A2238] text-sm font-medium">Simuler le vol de session</p>
                <p className="text-[#8B8470] text-xs">1 950,00 € · Moscou, depuis un appareil inconnu</p>
              </div>
              {loadingAction === "attack" && <span className="text-xs text-[#8B8470]">...</span>}
            </button>
          </div>
        </div>

        {/* Historique */}
        <div>
          <p className="text-[11px] font-semibold text-[#8B8470] uppercase tracking-wide mb-3">
            Transactions récentes
          </p>
          <div className="bg-white border border-[#E5DFC9] rounded-xl divide-y divide-[#EFE9D6]">
            {history.map((h) => (
              <div key={h.id} className="flex items-center justify-between px-4 py-3">
                <div>
                  <p className="text-[#1A2238] text-sm">{h.label}</p>
                  <p className="text-[#8B8470] text-xs">{h.date}</p>
                </div>
                <p
                  className={classNames(
                    "text-sm font-medium",
                    h.amount > 0 ? "text-emerald-600" : "text-[#1A2238]"
                  )}
                >
                  {h.amount > 0 ? "+" : ""}
                  {h.amount.toLocaleString("fr-FR", { minimumFractionDigits: 2 })} €
                </p>
              </div>
            ))}
          </div>
        </div>
      </main>

      {otpScenario && (
        <OtpModal
          scenario={otpScenario}
          onSubmit={handleOtpSubmit}
          sending={otpSending}
          error={otpError}
          expiresIn={90}
          onCancel={() => {
            setOtpScenario(null);
            setPendingTx(null);
            setOtpError("");
          }}
        />
      )}

      <ResultToast result={result} onClose={() => setResult(null)} />
    </div>
  );
}

// ───────────────────────────────────────────────────────────
// APP PRINCIPALE
// ───────────────────────────────────────────────────────────
export default function App() {
  const [token, setToken] = useState(null);
  const [apiStatus, setApiStatus] = useState("checking");

  useEffect(() => {
    fetch(`${API_URL}/docs`)
      .then(() => setApiStatus("online"))
      .catch(() => setApiStatus("offline"));
  }, []);

  if (!token) {
    return <LoginScreen onLogin={setToken} apiStatus={apiStatus} />;
  }

  return <BankDashboard token={token} onLogout={() => setToken(null)} />;
}
