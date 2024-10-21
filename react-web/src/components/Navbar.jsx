function Navbar({
  dashboardConnected,
  clientId,
  disconnect,
  reconnect,
  logout,
}) {
  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-dark sticky-top">
      <div className="container-fluid">
        <div className="me-auto d-flex">
          <a className="navbar-brand">&nbsp; AWS TwinMaker Dynamic Scenes Demo</a>
        </div>
        <div className="me-auto">
        </div>
        <div className="nav-item m-1 d-flex">
          {dashboardConnected && (
            <button className="btn btn-sm btn-normal mr-1" disabled>
              <span className="badge badge-success p-1 align-right">
                MQTT Client Connected: {clientId}
              </span>
            </button>
          )}
          {!dashboardConnected && (
            <button className="btn btn-sm btn-alt mr-1" disabled>
              <span className="badge btn-alt p-1 align-right">
                MQTT Not Connected
              </span>
            </button>
          )}
        </div>

        <div className="nav-item m-1 d-flex justify-content-end">
          <button
            className="btn btn-sm btn-outline-light"
            onClick={reconnect}
            disabled={dashboardConnected}
          >
            Connect MQTT
          </button>
        </div>
        <div className="nav-item m-1 d-flex justify-content-end">
          <button
            className="btn btn-sm btn-outline-light"
            onClick={disconnect}
            disabled={!dashboardConnected}
          >
            Disconnect MQTT
          </button>
        </div>
        <div className="nav-item m-1 d-flex justify-content-end">
          <button className="btn btn-sm btn-alt" onClick={logout}>
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
