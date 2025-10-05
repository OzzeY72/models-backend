import { useState } from "react";
import { api } from "../api";
import { useUser } from "../context/UserContext";

export default function EscortForm({ telegramId, is_top = false }) {
  const [form, setForm] = useState({
    name: "",
    age: "",
    phonenumber: "",
    address: "",
    height: "",
    weight: "",
    cupsize: "",
    bodytype: "Skinny",
    price_1h: "",
    price_2h: "",
    price_full_day: "",
    description: "",
    is_top: is_top,
    telegram_id: telegramId,
  });
  const [files, setFiles] = useState([]);
  const { refreshUser } = useUser();

  const handleChange = (key, value, isNumber = false) => {
    setForm((prev) => ({
      ...prev,
      [key]: isNumber && value !== "" ? parseFloat(value) : value,
    }));
  };

  const submit = async () => {
    try {
      const fd = new FormData();
      Object.entries(form).forEach(([key, val]) => fd.append(key, val));
      files.forEach((f) => fd.append("files", f));

      await api.post("/applications/", fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      await refreshUser();
      alert("✅ Model successfully created!");

      // 🔸 Редирект на главную
      window.location.href = "/";

      // 🔸 Если в Telegram WebApp — закрываем
      if (window.Telegram?.WebApp) {
        setTimeout(() => window.Telegram.WebApp.close(), 1500);
      }
    } catch (err) {
      console.error(err);
      alert("❌ Error while creating model");
    }
  };

  return (
    <div className="p-6 max-w-md mx-auto bg-white shadow-lg rounded-2xl border border-gray-200 space-y-5">
      <h2 className="text-xl font-semibold text-gray-800 text-center">
        💃 Create Model Profile
      </h2>

      {/* Поля формы */}
      <div className="space-y-4">
        {[
          { key: "name", label: "Name", type: "text", placeholder: "Enter name" },
          { key: "age", label: "Age", type: "number", placeholder: "Enter age" },
          { key: "phonenumber", label: "Phone number", type: "text", placeholder: "+1..." },
          { key: "address", label: "Address", type: "text", placeholder: "City, area..." },
          { key: "height", label: "Height (cm)", type: "number", placeholder: "170" },
          { key: "weight", label: "Weight (kg)", type: "number", placeholder: "55" },
          { key: "cupsize", label: "Cup size", type: "number", placeholder: "3" },
        ].map((field) => (
          <label key={field.key} className="block text-left">
            <span className="block text-sm text-gray-600">{field.label}</span>
            <input
              type={field.type}
              placeholder={field.placeholder}
              value={form[field.key]}
              onChange={(e) =>
                handleChange(field.key, e.target.value, field.type === "number")
              }
              className="w-full border border-gray-300 rounded-md p-2 mt-1 focus:ring-2 focus:ring-blue-400 outline-none"
            />
          </label>
        ))}

        {/* Body type */}
        <label className="block text-left">
          <span className="block text-sm text-gray-600">Body type</span>
          <select
            value={form.bodytype}
            onChange={(e) => handleChange("bodytype", e.target.value)}
            className="w-full border border-gray-300 rounded-md p-2 mt-1 focus:ring-2 focus:ring-blue-400 outline-none bg-white"
          >
            <option value="Skinny">Skinny</option>
            <option value="Slim">Slim</option>
            <option value="Athletic">Athletic</option>
            <option value="Curvy">Curvy</option>
          </select>
        </label>

        {/* Prices */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <label className="block text-left">
            <span className="block text-sm text-gray-600">1h (USD)</span>
            <input
              type="number"
              placeholder="150"
              value={form.price_1h}
              onChange={(e) => handleChange("price_1h", e.target.value, true)}
              className="w-full border border-gray-300 rounded-md p-2 mt-1 focus:ring-2 focus:ring-blue-400 outline-none"
            />
          </label>

          <label className="block text-left">
            <span className="block text-sm text-gray-600">2h (USD)</span>
            <input
              type="number"
              placeholder="250"
              value={form.price_2h}
              onChange={(e) => handleChange("price_2h", e.target.value, true)}
              className="w-full border border-gray-300 rounded-md p-2 mt-1 focus:ring-2 focus:ring-blue-400 outline-none"
            />
          </label>

          <label className="block text-left">
            <span className="block text-sm text-gray-600">Full day (USD)</span>
            <input
              type="number"
              placeholder="800"
              value={form.price_full_day}
              onChange={(e) =>
                handleChange("price_full_day", e.target.value, true)
              }
              className="w-full border border-gray-300 rounded-md p-2 mt-1 focus:ring-2 focus:ring-blue-400 outline-none"
            />
          </label>
        </div>

        {/* Description */}
        <label className="block text-left">
          <span className="block text-sm text-gray-600">Description</span>
          <textarea
            placeholder="Short description..."
            value={form.description}
            onChange={(e) => handleChange("description", e.target.value)}
            className="w-full border border-gray-300 rounded-md p-2 mt-1 h-24 resize-none focus:ring-2 focus:ring-blue-400 outline-none"
          />
        </label>

        {/* Upload photos */}
        <label className="block text-left">
          <span className="block text-sm text-gray-600">Upload photos</span>
          <input
            type="file"
            multiple
            accept="image/*"
            onChange={(e) => setFiles(Array.from(e.target.files))}
            className="w-full mt-2 border border-gray-300 rounded-md p-2 bg-gray-50 cursor-pointer"
          />
        </label>

        {/* Submit button */}
        <button
          onClick={submit}
          className="w-full bg-black text-white py-2.5 rounded-md font-medium hover:bg-gray-800 transition"
        >
          Submit
        </button>
      </div>
    </div>
  );
}
