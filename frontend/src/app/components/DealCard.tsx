import Image from "next/image";

interface DealProps {
  id: string;
  name: string;
  priceBTC: string;
  discount: string;
  image: string;
}

export default function DealCard({ name, priceBTC, discount, image }: DealProps) {
  return (
    <div className="p-4 bg-gray-800 rounded-lg shadow-lg hover:shadow-xl transition-shadow">
      <Image
        src={image}
        alt={name}
        width={300}
        height={200}
        className="rounded-md"
      />
      <h3 className="text-lg font-semibold mt-4">{name}</h3>
      <p className="text-xl text-neonGreen font-bold">{priceBTC} BTC</p>
      <p className="text-sm text-gray-400">{discount} OFF</p>
    </div>
  );
}
