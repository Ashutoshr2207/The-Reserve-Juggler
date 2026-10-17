import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles.css';
class Boundary extends React.Component<React.PropsWithChildren, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  render() { return this.state.failed ? <main className="fatal"><h1>The workspace could not be displayed.</h1><p>Your saved backend records remain available. Reload to reconnect.</p><button onClick={() => location.reload()}>Reload workspace</button></main> : this.props.children; }
}
ReactDOM.createRoot(document.getElementById('root')!).render(<React.StrictMode><Boundary><App /></Boundary></React.StrictMode>);
