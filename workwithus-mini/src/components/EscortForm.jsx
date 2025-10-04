import { useState } from "react";
import { api } from "../api";

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
  });
  const [files, setFiles] = useState([]);

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

      await api.post("/masters/", fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      alert("✅ Model successfully created!");
      if (window.Telegram?.WebApp) {
        window.Telegram.WebApp.close();
      }
    } catch (err) {
      console.error(err);
      alert("❌ Error while creating model");
    }
  };

  return (
    <div className="p-6 space-y-4 max-w-md mx-auto bg-white shadow rounded-xl">
      <h2 className="text-xl font-semibold mb-4">💃 Create Model Profile</h2>

      <label>
        Name:
        <input
          type="text"
          placeholder="Enter name"
          value={form.name}
          onChange={(e) => handleChange("name", e.target.value)}
        />
      </label>

      <label>
        Age:
        <input
          type="number"
          placeholder="Enter age"
          value={form.age}
          onChange={(e) => handleChange("age", e.target.value, true)}
        />
      </label>

      <label>
        Phone number:
        <input
          type="text"
          placeholder="+1..."
          value={form.phonenumber}
          onChange={(e) => handleChange("phonenumber", e.target.value)}
        />
      </label>

      <label>
        Address:
        <input
          type="text"
          placeholder="City, area..."
          value={form.address}
          onChange={(e) => handleChange("address", e.target.value)}
        />
      </label>

      <label>
        Height (cm):
        <input
          type="number"
          placeholder="170"
          value={form.height}
          onChange={(e) => handleChange("height", e.target.value, true)}
        />
      </label>

      <label>
        Weight (kg):
        <input
          type="number"
          placeholder="55"
          value={form.weight}
          onChange={(e) => handleChange("weight", e.target.value, true)}
        />
      </label>

      <label>
        Cup size:
        <input
          type="number"
          placeholder="3"
          value={form.cupsize}
          onChange={(e) => handleChange("cupsize", e.target.value, true)}
        />
      </label>

      <label>
        Body type:
        <select
          value={form.bodytype}
          onChange={(e) => handleChange("bodytype", e.target.value)}
        >
          <option value="Skinny">Skinny</option>
          <option value="Slim">Slim</option>
          <option value="Athletic">Athletic</option>
          <option value="Curvy">Curvy</option>
        </select>
      </label>

      <label>
        Price 1h (USD):
        <input
          type="number"
          placeholder="150"
          value={form.price_1h}
          onChange={(e) => handleChange("price_1h", e.target.value, true)}
        />
      </label>

      <label>
        Price 2h (USD):
        <input
          type="number"
          placeholder="250"
          value={form.price_2h}
          onChange={(e) => handleChange("price_2h", e.target.value, true)}
        />
      </label>

      <label>
        Price full day (USD):
        <input
          type="number"
          placeholder="800"
          value={form.price_full_day}
          onChange={(e) => handleChange("price_full_day", e.target.value, true)}
        />
      </label>

      <label>
        Description:
        <textarea
          placeholder="Short description..."
          value={form.description}
          onChange={(e) => handleChange("description", e.target.value)}
        />
      </label>

      <label>
        Upload photos:
        <input
          type="file"
          multiple
          accept="image/*"
          onChange={(e) => setFiles(Array.from(e.target.files))}
        />
      </label>

      <button
        className="bg-black text-white py-2 px-4 rounded-md hover:bg-gray-800"
        onClick={submit}
      >
        Submit
      </button>
    </div>
  );
}
