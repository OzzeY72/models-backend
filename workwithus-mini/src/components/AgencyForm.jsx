import { useState } from "react";
import { api } from "../api";

export default function AgencyForm({telegramId, is_agency = true}) {
  const [form, setForm] = useState({
    name: "",
    phone: "",
    address: "",
    is_agency: is_agency,
    model_count: 0,
  });
  const [files, setFiles] = useState([]);
  const [agencyId, setAgencyId] = useState(null);
  const [models, setModels] = useState([]);

  const handleChange = (field, value, isNumber = false) => {
    setForm({
      ...form,
      [field]: isNumber ? parseFloat(value) || 0 : value,
    });
  };

  const handleModelChange = (index, field, value, isNumber = false) => {
    const updated = [...models];
    updated[index] = {
      ...updated[index],
      [field]: isNumber ? parseFloat(value) || 0 : value,
    };
    setModels(updated);
  };

  const addModel = () => {
    setModels([
      ...models,
      {
        name: "",
        age: 0,
        phonenumber: "",
        address: "",
        height: 0,
        weight: 0,
        cupsize: 0,
        bodytype: "Skinny",
        price_1h: 0,
        price_2h: 0,
        price_full_day: 0,
        description: "",
        files: [],
      },
    ]);
  };

  const submitAgency = async () => {
    try {
      const fd = new FormData();
      Object.entries(form).forEach(([k, v]) => fd.append(k, v));
      files.forEach((f) => fd.append("files", f));

      const res = await api.post("/agencies/", fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      alert("✅ Agency created successfully!");
      setAgencyId(res.data.id);
    } catch (err) {
      console.error(err);
      alert("❌ Error creating agency");
    }
  };

  const submitModel = async (index) => {
    try {
      const model = models[index];
      const fd = new FormData();
      Object.entries(model).forEach(([k, v]) => {
        if (k !== "files") fd.append(k, v);
      });
      model.files.forEach((f) => fd.append("files", f));

      await api.post(`/agencies/${agencyId}/masters/`, fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      alert(`✅ Model #${index + 1} added successfully!`);
    } catch (err) {
      console.error(err);
      alert("❌ Error adding model");
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto space-y-6 font-sans">
      <h2 className="text-2xl font-semibold text-center">Create Agency / SPA</h2>

      {/* === Agency Form === */}
      <div className="space-y-3 border p-4 rounded-lg shadow-sm">
        <label>
          Agency Name:
          <input
            type="text"
            className="w-full border rounded p-2 mt-1"
            placeholder="Luxury SPA"
            value={form.name}
            onChange={(e) => handleChange("name", e.target.value)}
          />
        </label>

        <label>
          Phone number:
          <input
            type="text"
            className="w-full border rounded p-2 mt-1"
            placeholder="+1 555 123 456"
            value={form.phone}
            onChange={(e) => handleChange("phone", e.target.value)}
          />
        </label>

        <label>
          Address:
          <input
            type="text"
            className="w-full border rounded p-2 mt-1"
            placeholder="City, area..."
            value={form.address}
            onChange={(e) => handleChange("address", e.target.value)}
          />
        </label>

        <label>
          Number of models:
          <select
            className="w-full border rounded p-2 mt-1"
            value={form.model_count}
            onChange={(e) => handleChange("model_count", e.target.value, true)}
          >
            <option value={5}>Up to 5</option>
            <option value={9}>5-9</option>
            <option value={15}>10-15</option>
            <option value={100}>15+</option>
          </select>
        </label>

        <label>
          Upload agency logo/photo:
          <input
            type="file"
            multiple
            className="w-full mt-1"
            onChange={(e) => setFiles(Array.from(e.target.files))}
          />
        </label>

        <button
          onClick={submitAgency}
          className="bg-blue-500 text-white rounded px-4 py-2 w-full mt-2 hover:bg-blue-600"
        >
          Create Agency
        </button>
      </div>

      {/* === Models Section === */}
      {agencyId && (
        <div className="space-y-6">
          <h3 className="text-xl font-semibold text-center">
            Add Models to Agency
          </h3>
          {models.map((m, i) => (
            <div
              key={i}
              className="border rounded-lg p-4 space-y-3 bg-gray-50 shadow-sm"
            >
              <h4 className="font-medium">Model #{i + 1}</h4>

              {[
                ["Name", "name"],
                ["Age", "age", true],
                ["Phone number", "phonenumber"],
                ["Address", "address"],
                ["Height (cm)", "height", true],
                ["Weight (kg)", "weight", true],
                ["Cup size", "cupsize", true],
              ].map(([label, field, isNum]) => (
                <label key={field} className="block">
                  {label}:
                  <input
                    type={isNum ? "number" : "text"}
                    className="w-full border rounded p-2 mt-1"
                    value={m[field]}
                    onChange={(e) =>
                      handleModelChange(i, field, e.target.value, isNum)
                    }
                  />
                </label>
              ))}

              <label>
                Body type:
                <select
                  className="w-full border rounded p-2 mt-1"
                  value={m.bodytype}
                  onChange={(e) =>
                    handleModelChange(i, "bodytype", e.target.value)
                  }
                >
                  <option value="Skinny">Skinny</option>
                  <option value="Slim">Slim</option>
                  <option value="Athletic">Athletic</option>
                  <option value="Curvy">Curvy</option>
                </select>
              </label>

              {[
                ["Price 1h (USD)", "price_1h"],
                ["Price 2h (USD)", "price_2h"],
                ["Price full day (USD)", "price_full_day"],
              ].map(([label, field]) => (
                <label key={field} className="block">
                  {label}:
                  <input
                    type="number"
                    className="w-full border rounded p-2 mt-1"
                    value={m[field]}
                    onChange={(e) =>
                      handleModelChange(i, field, e.target.value, true)
                    }
                  />
                </label>
              ))}

              <label>
                Description:
                <textarea
                  className="w-full border rounded p-2 mt-1"
                  placeholder="Short description..."
                  value={m.description}
                  onChange={(e) =>
                    handleModelChange(i, "description", e.target.value)
                  }
                />
              </label>

              <label>
                Upload photos:
                <input
                  type="file"
                  multiple
                  className="w-full mt-1"
                  onChange={(e) =>
                    handleModelChange(
                      i,
                      "files",
                      Array.from(e.target.files),
                      false
                    )
                  }
                />
              </label>

              <button
                onClick={() => submitModel(i)}
                className="bg-green-500 text-white rounded px-4 py-2 w-full mt-2 hover:bg-green-600"
              >
                Add Model
              </button>
            </div>
          ))}

          <button
            onClick={addModel}
            className="bg-gray-700 text-white rounded px-4 py-2 w-full mt-3 hover:bg-gray-800"
          >
            + Add Another Model
          </button>
        </div>
      )}
    </div>
  );
}
