import { useEffect, useState } from "react";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";
import { useUser } from "../context/UserContext"; // 👈 добавили

export default function VerifyForm({ onVerified }) {
  const tg = window.Telegram.WebApp;
  const userTg = tg.initDataUnsafe?.user;
  const { token, user, saveAuth } = useAuth();
  const { refreshUser } = useUser(); // 👈 добавили

  const [telegramId, setTelegramId] = useState(userTg?.id?.toString() || "");
  const [phone, setPhone] = useState("");
  const [code, setCode] = useState("");
  const [stage, setStage] = useState("register");
  const [loading, setLoading] = useState(false);

  // 🔸 Если токен уже есть — сразу завершаем верификацию
  useEffect(() => {
    if (token && user) {
      console.log("✅ Already verified:", user);
      onVerified(user);
    }
  }, [token, user, onVerified]);

  const register = async () => {
    try {
      setLoading(true);
      await api.post("/auth/register", {
        telegram_id: telegramId,
        phonenumber: phone,
      });
      setStage("verify");
    } catch (err) {
      console.error(err);
      alert("❌ Failed to send OTP");
    } finally {
      setLoading(false);
    }
  };

  const verify = async () => {
    try {
      setLoading(true);
      const res = await api.post("/auth/verify", {
        telegram_id: telegramId,
        code,
      });

      // сохраняем токен и юзера в AuthContext
      saveAuth(res.data.token, res.data.user);

      // обновляем данные в UserContext
      await refreshUser();

      onVerified(res.data.user);
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.message || "❌ Verification failed");
    } finally {
      setLoading(false);
    }
  };

  if (token && user) {
    return (
      <div className="p-6 text-center text-gray-600">
        🔄 Logging you in...
      </div>
    );
  }

  return (
    <div className="p-6 max-w-sm mx-auto border rounded-lg shadow-sm bg-white space-y-4 font-sans">
      {stage === "register" ? (
        <>
          <h2 className="text-2xl font-semibold text-center">📱 Sign up</h2>
          <label className="block">
            Phone number:
            <input
              type="text"
              placeholder="+123456789"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="w-full border rounded p-2 mt-1"
            />
          </label>

          <button
            onClick={register}
            disabled={loading}
            className={`w-full rounded px-4 py-2 text-white font-medium transition ${
              loading
                ? "bg-gray-400 cursor-not-allowed"
                : "bg-blue-500 hover:bg-blue-600"
            }`}
          >
            {loading ? "Sending..." : "Get OTP"}
          </button>
        </>
      ) : (
        <>
          <h2 className="text-2xl font-semibold text-center">
            Enter code from WhatsApp
          </h2>
          <label className="block">
            6-digit code:
            <input
              type="text"
              placeholder="123456"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              className="w-full border rounded p-2 mt-1 tracking-widest text-center"
            />
          </label>

          <button
            onClick={verify}
            disabled={loading}
            className={`w-full rounded px-4 py-2 text-white font-medium transition ${
              loading
                ? "bg-gray-400 cursor-not-allowed"
                : "bg-green-500 hover:bg-green-600"
            }`}
          >
            {loading ? "Verifying..." : "Submit"}
          </button>
        </>
      )}
    </div>
  );
}
