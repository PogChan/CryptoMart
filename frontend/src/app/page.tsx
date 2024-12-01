// src/app/page.tsx
import ProductGrid from "@/app/components/ProductGrid";
import { fetchHotDeals } from "@/utils/api";


export default async function HomePage() {
  const hotDeals = await fetchHotDeals();

  return (
    <section>
      <h1 className="text-3xl font-bold text-neonGreen mb-6">Welcome to CryptoMart</h1>
      <ProductGrid deals={hotDeals} />
    </section>
  );
}
