import { useState } from "react";
import { Route, BrowserRouter as Router, Routes } from "react-router-dom";

import AgencyForm from "./components/AgencyForm";
import EscortForm from "./components/EscortForm";
import SelectType from "./components/SelectType";
import VerifyForm from "./components/VerifyForm";
import ProfileRoute from "./pages/ProfileRoute";

export default function App() {
  const [step, setStep] = useState("verify");
  const [userType, setUserType] = useState("");
  const [telegramId, setTelegramId] = useState("");

  return (
    <Router>
      <Routes>
        {/* Route для просмотра существующих профилей */}
        <Route path="/profile/:id" element={<ProfileRoute />} />

        {/* Главный flow регистрации/создания анкеты */}
        <Route
          path="/*"
          element={
            <div className="p-6 max-w-md mx-auto text-center">
              {step === "verify" && (
                <VerifyForm
                  onVerified={(id) => {
                    setTelegramId(id);
                    setStep("select-type");
                  }}
                />
              )}

              {step === "select-type" && (
                <SelectType
                  onSelect={(type) => {
                    setUserType(type);
                    setStep("form");
                  }}
                />
              )}

              {step === "form" && (
                <>
                  {userType === "escort" && (
                    <EscortForm telegramId={telegramId} is_top={false} />
                  )}
                  {userType === "top" && (
                    <EscortForm telegramId={telegramId} is_top={true} />
                  )}
                  {userType === "agency" && (
                    <AgencyForm telegramId={telegramId} is_agency={true} />
                  )}
                  {userType === "spa" && (
                    <AgencyForm telegramId={telegramId} is_agency={false} />
                  )}
                </>
              )}
            </div>
          }
        />
      </Routes>
    </Router>
  );
}
