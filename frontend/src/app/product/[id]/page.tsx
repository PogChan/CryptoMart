// src/app/product/[id]/page.tsx
import { fetchProductById } from "@/utils/api";
import Image from "next/image";
export default async function ProductPage({ params }: { params: { id: string } }) {
  const product = await fetchProductById(params.id); // Fetch product data

  return (
    <div>
      <Image src={product.image} alt={product.name} className="w-full h-64 object-cover mb-4 rounded-md" />
      <h1 className="text-2xl mb-2">{product.name}</h1>
      <p className="text-lg text-neonGreen">{product.priceBTC} BTC</p>
      <p className="text-gray-400">{product.discount} OFF</p>
      <p className="mt-4">{product.description}</p>
    </div>
  );
}
