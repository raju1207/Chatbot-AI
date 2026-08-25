export default function MessageBubble({role, children}){ return <div className={`message ${role}`}>{children}</div> }
