import AlertsList from "@/components/AlertsList";

export default function AlertsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-zinc-900 via-zinc-950 to-indigo-950 p-0 md:p-8 flex flex-col items-center font-sans pb-32 md:pb-16">
      <div className="w-full max-w-7xl rounded-none md:rounded-2xl shadow-2xl bg-white/10 backdrop-blur-md border border-zinc-800 p-0 md:p-8 mt-0 md:mt-8 min-h-screen md:min-h-0">
        <div className="w-full flex flex-col items-center mb-6 mt-2">
          <h1 className="text-3xl md:text-4xl font-bold text-white mb-1 drop-shadow-lg">Smart Alerts</h1>
          <p className="text-zinc-300 text-base md:text-lg">Stay informed about your investments.</p>
        </div>
        <div className="space-y-6 md:space-y-8 p-4 md:p-0 mb-8 md:mb-12">
          <AlertsList />
        </div>
      </div>
    </div>
  );
}