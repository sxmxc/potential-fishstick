import Layout from "../components/Layout";
import SignalBadge from "../components/SignalBadge";

export default function Home() {
  const demo = [
    { id: "1", title: "ETH −8% in 15m", score: 0.78 },
    { id: "2", title: "RHR z=2.3 for 4d", score: 0.64 },
  ];
  return (
    <Layout>
      <h1 style={{ fontSize: 20, fontWeight: 600, marginBottom: 12 }}>What matters now</h1>
      <div>
        {demo.map((e) => (
          <div key={e.id} style={{ border: '1px solid #ddd', borderRadius: 12, padding: 12, marginBottom: 10 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>{e.title}</div>
              <SignalBadge score={e.score} />
            </div>
          </div>
        ))}
      </div>
    </Layout>
  );
}
