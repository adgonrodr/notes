{
  "query": "query MissingAttributeToColumn($entityId: UUID!, $entityToAttributeRel: String!, $attributeToColumnRel: String!, $limit: Int = 200, $offset: Int = 0) { missingAttributes: assets(limit: $limit, offset: $offset, where: { _and: [ { incomingRelations: { any: { source: { id: { eq: $entityId } }, type: { publicId: { eq: $entityToAttributeRel } } } } }, { outgoingRelations: { typePublicId: $attributeToColumnRel, empty: true } } ] }) { id fullName displayName } }",
  "variables": {
    "entityId": "00000000-0000-0000-0000-000000000000",
    "entityToAttributeRel": "ENTITY_TO_ATTRIBUTE_REL_PUBLIC_ID",
    "attributeToColumnRel": "ATTRIBUTE_TO_COLUMN_REL_PUBLIC_ID",
    "limit": 200,
    "offset": 0
  }
}