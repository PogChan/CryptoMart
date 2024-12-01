// src/app/components/Header.tsx
export default function Header() {
  return (
    <header className="p-4 bg-gray-900 text-white flex justify-between items-center shadow-md">
      <h1 className="text-2xl font-bold text-neonGreen">CryptoMart</h1>
      <input
        type="text"
        placeholder="Search products..."
        className="px-4 py-2 rounded-md bg-gray-800 text-white placeholder-gray-400 w-1/3"
      />
    </header>
  );
}
