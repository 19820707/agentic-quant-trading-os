# Governance Schemas

Governance schemas define approval state, evidence references, promotion gates,
owner boundaries and rollback metadata.

`CapabilityManifest` maps repository capabilities to maturity state, allowed
behavior, forbidden behavior, required contracts, required tests and approval
gates. It is a control-plane contract only and does not enable runtime,
network access, credentials, trading or production use.

