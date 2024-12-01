export async function fetchHotDeals() {
  // Mock API call
  return [
    { id: "1", name: "Wireless Headphones", priceBTC: "0.005", discount: "20%", image: "/images/headphones.jpg" },
    { id: "2", name: "Gaming Console", priceBTC: "0.08", discount: "15%", image: "/images/console.jpg" },
  ];
}

export async function fetchProductById(id: string) {
  // Mock API call for product details
  return {
    id,
    name: "Wireless Headphones",
    priceBTC: "0.005",
    discount: "20%",
    description: "High-quality wireless headphones with noise cancellation.",
    image: "/images/headphones.jpg",
  };
}
