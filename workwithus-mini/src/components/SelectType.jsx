export default function SelectType({ onSelect }) {
  return (
    <div className="p-4">
      <h2>What type of service you want to registrate?</h2>
      <div className="flex flex-col gap-2">
        <button onClick={() => onSelect("top")}>💃 Top Escort</button>
        <button onClick={() => onSelect("escort")}>💃 Escort</button>
        <button onClick={() => onSelect("agency")}>🏢 Agency</button>
        <button onClick={() => onSelect("spa")}>💆 SPA</button>
      </div>
    </div>
  );
}
