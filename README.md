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

---

{
  "query": "query($entityId: UUID!){ assets(where:{ id:{ eq:$entityId }}){ id fullName displayName type{ publicId } domain{ name } } }",
  "variables": {
    "entityId": "PUT_ENTITY_UUID_HERE"
  }
}

---

{
  "query": "query($entityId: UUID!, $limit: Int!){ assets(where:{ id:{ eq:$entityId }}){ fullName outgoingRelations(limit:$limit){ type{ publicId } target{ id fullName type{ publicId } } } incomingRelations(limit:$limit){ type{ publicId } source{ id fullName type{ publicId } } } } }",
  "variables": {
    "entityId": "PUT_ENTITY_UUID_HERE",
    "limit": 50
  }
}

---

{
  "query": "query($entityId: UUID!, $entityToAttrRel: String!){ assets(where:{ id:{ eq:$entityId }}){ fullName attrs: outgoingRelations(where:{ type:{ publicId:{ eq:$entityToAttrRel }}}){ target{ id fullName displayName type{ publicId } } } } }",
  "variables": {
    "entityId": "PUT_ENTITY_UUID_HERE",
    "entityToAttrRel": "PUT_ENTITY_TO_ATTRIBUTE_REL_PUBLIC_ID"
  }
}

---

{
  "query": "query($entityId: UUID!, $entityToAttrRel: String!){ attrs: assets(where:{ incomingRelations:{ any:{ source:{ id:{ eq:$entityId } } type:{ publicId:{ eq:$entityToAttrRel } } } } }){ id fullName displayName type{ publicId } } }",
  "variables": {
    "entityId": "PUT_ENTITY_UUID_HERE",
    "entityToAttrRel": "PUT_ENTITY_TO_ATTRIBUTE_REL_PUBLIC_ID"
  }
}

---

{
  "query": "query($attrId: UUID!, $limit: Int!){ assets(where:{ id:{ eq:$attrId }}){ fullName type{ publicId } outgoingRelations(limit:$limit){ type{ publicId } target{ id fullName type{ publicId } } } incomingRelations(limit:$limit){ type{ publicId } source{ id fullName type{ publicId } } } } }",
  "variables": {
    "attrId": "PUT_ATTRIBUTE_UUID_HERE",
    "limit": 50
  }
}

---

{
  "query": "query($entityId: UUID!, $entityToAttrRel: String!, $attrToColRel: String!, $limit: Int!, $offset: Int!){ missing: assets(limit:$limit, offset:$offset, where:{ _and:[ { incomingRelations:{ any:{ source:{ id:{ eq:$entityId } } type:{ publicId:{ eq:$entityToAttrRel } } } } }, { outgoingRelations:{ typePublicId:$attrToColRel, empty:true } } ] }){ id fullName displayName } }",
  "variables": {
    "entityId": "PUT_ENTITY_UUID_HERE",
    "entityToAttrRel": "PUT_ENTITY_TO_ATTRIBUTE_REL_PUBLIC_ID",
    "attrToColRel": "PUT_ATTRIBUTE_TO_COLUMN_REL_PUBLIC_ID",
    "limit": 200,
    "offset": 0
  }
}

---

{
  "query": "query($entityId: UUID!, $entityToAttrRel: String!, $attrToColRel: String!, $limit: Int!, $offset: Int!){ missing: assets(limit:$limit, offset:$offset, where:{ _and:[ { incomingRelations:{ any:{ source:{ id:{ eq:$entityId } } type:{ publicId:{ eq:$entityToAttrRel } } } } }, { incomingRelations:{ typePublicId:$attrToColRel, empty:true } } ] }){ id fullName displayName } }",
  "variables": {
    "entityId": "PUT_ENTITY_UUID_HERE",
    "entityToAttrRel": "PUT_ENTITY_TO_ATTRIBUTE_REL_PUBLIC_ID",
    "attrToColRel": "PUT_ATTRIBUTE_TO_COLUMN_REL_PUBLIC_ID",
    "limit": 200,
    "offset": 0
  }
}

---


{
  "query": "query EntityDataAttributesTermsAndFlags($entityId: UUID!, $entityToAttrRel: String!, $piiAttrType: String!, $cdeAttrType: String!, $attrToBtRel: String!, $attrFirst: Int!, $attrAfter: String) { assets(where: { id: { eq: $entityId } }) { nodes { id fullName attrs: outgoingRelations(where: { type: { publicId: { eq: $entityToAttrRel } } }, first: $attrFirst, after: $attrAfter) { pageInfo { endCursor hasNextPage } nodes { target { id fullName displayName pii: attributes(where: { type: { publicId: { eq: $piiAttrType } } }) { nodes { id value } } cde: attributes(where: { type: { publicId: { eq: $cdeAttrType } } }) { nodes { id value } } businessTerms: outgoingRelations(where: { type: { publicId: { eq: $attrToBtRel } } }) { nodes { target { id fullName displayName type { publicId } } } } } } } } } } }",
  "variables": {
    "entityId": "PUT_ENTITY_UUID_HERE",
    "entityToAttrRel": "ENTITY_TO_DATA_ATTRIBUTE_REL_PUBLIC_ID",
    "piiAttrType": "PII_ATTRIBUTE_TYPE_PUBLIC_ID",
    "cdeAttrType": "CDE_ATTRIBUTE_TYPE_PUBLIC_ID",
    "attrToBtRel": "DATA_ATTRIBUTE_TO_BUSINESS_TERM_REL_PUBLIC_ID",
    "attrFirst": 200,
    "attrAfter": null
  }
}

