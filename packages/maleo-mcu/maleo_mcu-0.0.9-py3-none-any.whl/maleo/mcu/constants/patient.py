from maleo.schemas.resource import Resource, ResourceIdentifier

CLIENT_RESOURCE = Resource(
    identifiers=[ResourceIdentifier(key="patient", name="Patient", slug="patients")],
    details=None,
)
