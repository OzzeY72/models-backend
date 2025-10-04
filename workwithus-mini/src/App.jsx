import { useState } from "react";
import AgencyForm from "./components/AgencyForm";
import EscortForm from "./components/EscortForm";
import SelectType from "./components/SelectType";
import VerifyForm from "./components/VerifyForm";

export default function App() {
  const [step, setStep] = useState("verify");
  const [userType, setUserType] = useState("");
  const [telegramId, setTelegramId] = useState("");

  return (
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
          {userType === "escort" && <EscortForm telegramId={telegramId} is_top={false}/>}
          {userType === "top" && <EscortForm telegramId={telegramId} is_top={true} />}
          {userType === "agency" && <AgencyForm telegramId={telegramId} is_agency={true}/>}
          {userType === "spa" && <AgencyForm telegramId={telegramId} is_agency={false} />}
        </>
      )}
    </div>
  );
}
