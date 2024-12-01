// src/app/layout.tsx
import "@/app/styles/globals.css";
import Header from "@/app/components/Header";
import Footer from "@/app/components/Footer";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen flex flex-col">
          <Header />
          <main className="flex-grow p-8">{children}</main>
          <Footer />
        </div>
      </body>
    </html>
  );
}
