 delete shopify_product_data
   from shopify_product_data
  inner join (
     select max(id) as lastId, shopify_id
       from shopify_product_data
      group by shopify_id
     having count(*) > 1) duplic on duplic.shopify_id = shopify_product_data.shopify_id
  where shopify_product_data.id < duplic.lastId;