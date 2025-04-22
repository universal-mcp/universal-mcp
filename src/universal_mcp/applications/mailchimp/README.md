
# Mailchimp MCP Server

An MCP Server for the Mailchimp API.

## Supported Integrations

- AgentR
- API Key (Coming Soon)
- OAuth (Coming Soon)

## Tools

This is automatically generated from OpenAPI schema for the Mailchimp API.

## Supported Integrations

This tool can be integrated with any service that supports HTTP requests.

## Tool List

| Tool | Description |
|------|-------------|
| root_list_resources | Lists available resources by making a GET request to the base URL. |
| activity_feed_get_latest_chimp_chatter | Fetches the latest Chimp Chatter from the activity feed. |
| account_exports_list_for_given_account | Retrieves a list of account export jobs for the current account, with optional filtering and pagination. |
| account_exports_create_new_export | Creates a new account export job with configurable stages and an optional starting timestamp. |
| account_export_info | Retrieves detailed information about a specific account export. |
| authorized_apps_list_connected_applications | Retrieves a list of connected authorized applications with optional filtering and pagination. |
| authorized_apps_get_info | Retrieve detailed information about an authorized application by its ID. |
| automations_list_summary | Retrieves a summary list of automation workflows based on optional filtering, pagination, and field selection criteria. |
| automations_create_classic | Creates a classic automation by sending a POST request with the specified recipients and trigger settings. |
| automations_get_classic_workflow_info | Retrieves information about a classic automation workflow by its unique workflow ID. |
| automations_pause_workflow_emails | Pauses all workflow emails for a specified automation workflow. |
| automations_start_all_emails | Starts all email actions within the specified automation workflow. |
| automations_archive_action | Archives an automation workflow by sending a POST request to the specified API endpoint. |
| automations_get_classic_workflow_emails | Retrieves the list of emails associated with a classic workflow for a given workflow ID. |
| automations_get_email_info | Retrieves information about a specific email within a workflow automation, given the workflow and email identifiers. |
| automations_delete_workflow_email | Deletes a specific email from a workflow in the automations system. |
| automations_update_workflow_email | Updates the settings and delay of a specific workflow email in an automation workflow. |
| automations_list_queue_emails | Retrieves the list of queued emails for a specific workflow email in an automation. |
| automations_add_subscriber_to_workflow_email | Adds a subscriber to a specific workflow email queue in the automations system by sending a POST request. |
| automations_classic_automation_subscriber_info | Retrieves detailed information about a specific subscriber in a classic automation email workflow. |
| automations_pause_automated_email | Pauses an automated email within a specified workflow by sending a POST request to the automation API. |
| automations_start_automated_email | Starts an automated email within a specified workflow using the provided workflow and email identifiers. |
| automations_get_removed_subscribers | Retrieves the list of subscribers who have been removed from a specified automation workflow. |
| automations_remove_subscriber_from_workflow | Removes a subscriber from a specified automation workflow. |
| automations_get_removed_subscriber_info | Retrieves information about a subscriber who was removed from a specific automation workflow. |
| batches_list_requests_summary | Retrieves a summary of existing batch requests with optional field selection, exclusion, pagination, and filtering. |
| batches_start_operation_process | Starts a batch operation by sending the given operations to the remote service and returns the operation response as a dictionary. |
| batches_get_operation_status | Retrieves the status and details of a batch operation using its batch ID. |
| batches_stop_request | Stops a running batch job by sending a DELETE request to the batch endpoint. |
| batch_webhooks_list_webhooks | Retrieves a list of batch webhooks with optional filtering and pagination. |
| batch_webhooks_add_webhook | Adds a new webhook to the batch webhooks endpoint. |
| batch_webhooks_get_info | Retrieves information about a specific batch webhook. |
| batch_webhooks_update_webhook | Updates the configuration of a batch webhook by ID, modifying its URL and/or enabled status. |
| batch_webhooks_remove_webhook | Removes a webhook associated with a given batch webhook ID. |
| template_folders_list_folders | Retrieves a list of template folders with optional filtering and pagination parameters. |
| template_folders_add_new_folder | Creates a new template folder using the provided request body and returns the server's response. |
| template_folders_get_info | Retrieves information about a specific template folder. |
| template_folders_update_specific_folder | Updates a specific template folder with new data using a PATCH request. |
| template_folders_delete_specific_folder | Deletes a specific template folder identified by its folder_id. |
| campaign_folders_list_campaign_folders | Retrieves a list of campaign folders with optional filtering and pagination. |
| campaign_folders_add_new_folder | Creates a new campaign folder by sending a POST request with the provided data. |
| campaign_folders_get_folder_info | Retrieves information about a specific campaign folder by its unique identifier. |
| campaign_folders_update_specific_folder | Updates a specific campaign folder by ID. |
| campaign_folders_delete_folder | Deletes a campaign folder by its unique identifier. |
| campaigns_get_all | Retrieves all campaigns from the API with optional filtering and pagination. |
| campaigns_create_new_mailchimp_campaign | Creates a new Mailchimp campaign with the specified type and optional configuration settings. |
| campaigns_get_info | Retrieves detailed information about a specific campaign, supporting optional field filtering and resend shortcut eligibility inclusion. |
| campaigns_update_settings | Updates the settings of an email campaign with the specified parameters. |
| campaigns_remove_campaign | Removes a campaign identified by the given campaign ID. |
| campaigns_cancel_send_action | Cancels the scheduled sending of a campaign identified by its campaign ID. |
| campaigns_replicate_action | Replicates an existing campaign by sending a replicate action request to the API. |
| campaigns_send_action | Triggers the send action for a specified email campaign. |
| campaigns_schedule_delivery | Schedules the delivery of an email campaign at a specified time, with optional timewarp and batch delivery settings. |
| campaigns_unschedule_action | Unschedules an active campaign by sending a POST request to the campaign's unschedule action endpoint. |
| campaigns_send_test_email | Sends a test email for a specific campaign to a list of test email addresses. |
| campaigns_pause_rss_campaign | Pauses an RSS campaign by sending a pause action request to the campaign API endpoint. |
| campaigns_resume_rss_campaign | Resumes an RSS campaign with the specified ID. |
| campaigns_resend_action | Initiates a resend action for a specified campaign using the provided campaign ID and optional shortcut type. |
| campaigns_get_content | Retrieves the content of a specific campaign, with optional field filtering. |
| campaigns_set_content | Updates the content of a specific campaign with provided data such as plain text, HTML, URL, template, archive, or variate content. |
| campaigns_list_feedback | Retrieves feedback information for a specific email campaign, with optional field filtering. |
| campaigns_add_feedback | Submit feedback for a specific campaign by sending a message and optional metadata. |
| campaigns_get_feedback_message | Retrieves a specific feedback message for a given campaign, with optional field filtering. |
| campaigns_update_feedback_message | Updates the feedback message for a specified campaign and feedback entry. |
| campaigns_remove_feedback_message | Removes a specific feedback message from a campaign. |
| campaigns_get_send_checklist | Retrieves the send checklist for a specified campaign, optionally filtering the response fields. |
| connected_sites_list_all | Retrieves a list of all connected sites with optional filtering, field selection, and pagination. |
| connected_sites_create_new_mailchimp_site | Creates a new connected site in Mailchimp with the specified foreign ID and domain. |
| connected_sites_get_info | Retrieve detailed information for a specific connected site by ID, with optional field filtering. |
| connected_sites_remove_site | Removes a connected site by its unique identifier. |
| connected_sites_verify_script_installation | Verifies whether the tracking script is properly installed on a specified connected site. |
| conversations_get_all_conversations | Get all conversations from the API. |
| conversations_get_by_id | Retrieve the details of a conversation by its unique identifier. |
| conversations_list_messages_from_conversation | Retrieves messages from a specified conversation. |
| conversations_get_message_by_id | Retrieve a specific message from a conversation by its ID, with optional control over included and excluded fields. |
| customer_journeys_trigger_step_action | Triggers a specific action for a step in a customer journey for the given email address. |
| file_manager_upload_file | Uploads a file to the file manager service, associating it with a specified name and optionally a folder. |
| file_manager_get_file | Retrieves the details of a file from the file manager by its unique ID, optionally including or excluding specific fields. |
| file_manager_update_file | Updates the specified file's metadata in the file manager, such as its folder or name. |
| file_manager_remove_file_by_id | Removes a file from the file manager by its unique identifier. |
| file_manager_get_folder_list | Retrieves a list of folders from the file manager using optional filtering, field selection, and pagination parameters. |
| file_manager_add_new_folder | Creates a new folder in the file manager using the provided request body data. |
| file_manager_get_folder_info | Retrieves information about a specific folder from the file manager service. |
| file_manager_update_specific_folder | Updates a specific folder in the file manager system. |
| file_manager_delete_folder_by_id | Deletes a folder from the file manager by its unique identifier. |
| lists_get_all_info | Retrieves detailed information about all lists, with support for filtering, sorting, and field selection. |
| lists_create_new_list | Creates a new mailing list with the specified parameters and returns the created list's details. |
| lists_get_list_info | Retrieves detailed information about a specific list, including optional field selection and total contacts count. |
| lists_update_settings | Updates the settings of a specified mailing list with provided configuration details. |
| lists_delete_list | Deletes a list with the specified list ID via a DELETE request and returns the server's response as JSON. |
| lists_batch_subscribe_or_unsubscribe | Batch subscribes or unsubscribes members to a specified mailing list, with optional parameters for merge validation, duplicate checking, tag synchronization, and updating existing members. |
| lists_get_all_abuse_reports | Retrieves all abuse reports for a specific list, with optional filtering and pagination. |
| lists_get_abuse_report | Retrieves the details of a specific abuse report for a list. |
| lists_get_recent_activity_stats | Retrieves recent activity statistics for a specified list, with optional filtering and field selection. |
| lists_list_top_email_clients | Retrieves a summary of the top email clients for a specified email list. |
| lists_get_growth_history_data | Retrieves the growth history data for a specific list with optional filtering, sorting, and field selection. |
| lists_get_growth_history_by_month | Retrieves the growth history of a specific mailing list for a given month, with optional field filtering. |
| lists_list_interest_categories | Retrieves a list of interest categories for a specific mailing list, with optional filters and pagination. |
| lists_add_interest_category | Adds an interest category to a specified list by making a POST request to the list's interest-categories endpoint. |
| lists_get_interest_category_info | Retrieves detailed information about a specific interest category for a given Mailchimp list. |
| lists_update_interest_category | Updates an interest category for a specific list using the provided data. |
| lists_delete_interest_category | Deletes an interest category from a specified list using the provided IDs. |
| lists_list_category_interests | Retrieves all interests (subcategories) for a specific interest category within a Mailchimp list. |
| lists_add_interest_in_category | Adds a new interest to a specified interest category within a list. |
| lists_get_interest_in_category | Retrieves interest information within a category of a list. |
| lists_update_interest_category_interest | Updates a specific interest within an interest category for a given list by sending a PATCH request to the API. |
| lists_delete_interest_in_category | Deletes a specific interest from a given interest category within a mailing list. |
| lists_get_segments_info | Retrieves information about segments for a specific list, with support for filtering and pagination options. |
| lists_add_new_segment | Creates a new segment for a specified list, optionally as a static segment, by sending a POST request to the appropriate API endpoint. |
| lists_get_segment_info | Retrieves detailed information about a specific segment within a mailing list, allowing for optional filtering and inclusion of additional segment data. |
| lists_delete_segment | Deletes a specific segment from a list by its list and segment identifiers. |
| lists_update_segment_by_id | Updates a specific segment within a list using the provided identifiers and parameters. |
| lists_batch_add_remove_members | Adds and/or removes members in bulk to a specific segment within a given list. |
| lists_get_segment_members | Retrieve members of a specific segment within a list, with support for filtering and pagination options. |
| lists_add_member_to_segment | Adds a member to a specified segment within a mailing list. |
| lists_remove_member_from_segment | Removes a member from a segment within a specific list. |
| lists_search_tags_by_name | Searches for tags within a specific list by tag name using the list's unique identifier. |
| lists_get_members_info | Fetches and returns member information for a specified list by ID, allowing for various filtering and sorting options. |
| lists_add_member_to_list | Adds a member to a specified list with the provided details. |
| lists_get_member_info | Retrieve information about a specific list member from the Mailchimp API. |
| lists_add_or_update_member | Adds a new member to a list or updates an existing member's information in the specified list. |
| lists_update_member | Updates the information for a specific list member in the email marketing system, identified by list ID and subscriber hash, with the provided attributes. |
| lists_archive_member | Removes an archived member from a specified list using their unique subscriber hash. |
| lists_view_recent_activity_events | Retrieves recent activity events for a specific list member, optionally filtering the results by specified fields and actions. |
| lists_view_recent_activity | Retrieves recent activity for a specific subscriber in a mailing list. |
| lists_get_member_tags | Retrieves a list of tags assigned to a specific list member (subscriber) with optional filtering and pagination. |
| lists_add_member_tags | Adds member tags to a subscriber in a list. |
| lists_get_member_events | Retrieves member events for a specific subscriber in a mailing list. |
| lists_add_member_event | Adds a new event for a specific list member by sending a POST request with event details to the API. |
| lists_get_member_goals | Retrieves the goal information for a specific list member in Mailchimp. |
| lists_get_member_notes | Retrieves notes associated with a specific list member, with optional filtering, sorting, and pagination. |
| lists_add_member_note | Adds a note to a member of a mailing list. |
| lists_get_member_note | Retrieve a specific note associated with a list member from the remote API. |
| lists_update_note_specific_list_member | Updates a specific note for a list member in the email marketing platform. |
| lists_delete_note | Deletes a note associated with a specific subscriber in a list. |
| lists_remove_member_permanent | Permanently removes a member from a mailing list using their subscriber hash. |
| lists_list_merge_fields | Retrieves the list merge fields for a specified list, with optional filtering and pagination parameters. |
| lists_add_merge_field | Adds a new merge field to a specified mailing list. |
| lists_get_merge_field_info | Retrieves detailed information about a specific merge field within a list, allowing optional filtering of returned fields. |
| lists_update_merge_field | Updates an existing merge field for a specific list with the provided attributes. |
| lists_delete_merge_field | Deletes a merge field from a specified list by its merge field ID. |
| lists_get_webhooks_info | Retrieves webhook information for the specified list. |
| lists_create_webhook | Creates a new webhook for the specified list by sending a POST request to the API. |
| lists_get_webhook_info | Retrieves detailed information about a specific webhook for a given list. |
| lists_delete_webhook | Deletes a webhook from a specified list. |
| lists_update_webhook_settings | Updates the settings of a specific webhook associated with a list. |
| lists_get_signup_forms | Retrieves the signup forms associated with a specific list by its unique identifier. |
| lists_customize_signup_form | Customizes the signup form of a specific list by updating its header, contents, or styles via an API call. |
| lists_get_locations | Retrieves the locations associated with a specific list, optionally filtering the returned fields. |
| lists_get_surveys_info | Retrieves survey information associated with a specific list ID. |
| lists_get_survey_details | Retrieves the details of a specific survey associated with a given list by making an HTTP GET request. |
| surveys_publish_survey_action | Publishes a specified survey for a given list by sending a publish action request. |
| surveys_unpublish_survey_action | Unpublishes a survey for a specific mailing list. |
| surveys_generate_campaign | Creates an email campaign for a specific survey and list by triggering the appropriate API action. |
| landing_pages_list | Retrieves a list of landing pages from the API, supporting sorting, field selection, and result count customization. |
| landing_pages_create_new_mailchimp_landing_page | Creates a new Mailchimp landing page with the specified attributes. |
| landing_pages_get_page_info | Retrieves information about a specific landing page. |
| landing_pages_update_page_by_id | Updates the details of a landing page identified by its unique ID. |
| landing_pages_delete_page | Deletes a landing page resource identified by the given page ID. |
| landing_pages_publish_action | Publishes a landing page by sending a POST request to the publish action endpoint for the specified page ID. |
| landing_pages_unpublish_action | Unpublishes a landing page by sending a POST request to the corresponding unpublish action endpoint. |
| landing_pages_get_content | Fetches the content of a specified landing page, allowing optional filtering of fields to include or exclude. |
| reports_list_campaign_reports | Retrieves a list of campaign report summaries with optional filtering and pagination. |
| reports_specific_campaign_report | Retrieves a specific campaign report with optional field filtering. |
| reports_list_abuse_reports | Retrieves the list of abuse reports for a specified email campaign. |
| reports_get_abuse_report | Retrieve detailed information about a specific abuse report for a given campaign. |
| reports_list_campaign_feedback | Retrieves campaign feedback advice for a specified campaign report. |
| reports_get_campaign_click_details | Retrieves detailed click activity for a specific campaign report. |
| reports_specific_link_details | Retrieves detailed information about a specific link for a campaign. |
| reports_list_clicked_link_subscribers | Retrieves a list of subscribers who clicked a specific link in a campaign. |
| reports_specific_link_subscriber | Retrieves click report details for a specific subscriber who clicked a particular link in a campaign. |
| reports_list_campaign_open_details | Retrieves detailed open reports for a specific email campaign, with optional filtering, sorting, and pagination. |
| reports_open_subscriber_details | Retrieves detailed open report information for a specific subscriber in a given campaign. |
| reports_list_domain_performance_stats | Retrieves domain performance statistics for a specific campaign, with optional field filtering. |
| reports_list_eepurl_activity | Retrieves EepURL activity details for a specified campaign report. |
| reports_list_email_activity | Retrieves the email activity report for a specific campaign, with optional filtering and field selection. |
| reports_get_subscriber_activity | Gets the email activity for a specific subscriber in a campaign. |
| reports_list_top_open_locations | Retrieves a list of top open locations for a specific campaign report, with optional filtering, field selection, and pagination. |
| reports_list_campaign_recipients | Retrieves a list of recipients for a specific email campaign report. |
| reports_campaign_recipient_info | Retrieves detailed information about a recipient's interaction with a specific campaign report. |
| reports_list_child_campaign_reports | Lists child campaign reports for a specified campaign. |
| reports_list_unsubscribed_members | Retrieves a list of unsubscribed members for a specified campaign. |
| reports_get_unsubscribed_member_info | Retrieves information about a member who unsubscribed from a specific campaign report. |
| reports_get_campaign_product_activity | Retrieves ecommerce product activity reports for a specified campaign, with optional filtering, pagination, and sorting. |
| templates_list_available_templates | Retrieves a list of available email templates with optional filtering, sorting, and pagination. |
| templates_create_new_template | Creates a new template by sending a POST request to the templates endpoint. |
| templates_get_info | Retrieve detailed information about a specific template, with optional field filtering. |
| templates_update_template_by_id | Updates an existing template by its unique ID using provided data. |
| templates_delete_specific_template | Deletes a specific template identified by its template ID. |
| templates_view_default_content | Retrieves the default content for a specific template, optionally filtering included or excluded fields. |
| ecommerce_list_account_orders | Retrieves a list of ecommerce orders for the account with optional filtering and field selection. |
| ecommerce_list_stores | Retrieves a list of e-commerce stores accessible to the authenticated user, with optional filtering and pagination. |
| ecommerce_add_store_to_mailchimp_account | Adds an ecommerce store to a Mailchimp account using the provided parameters. |
| ecommerce_get_store_info | Fetches information about a specific e-commerce store, allowing optional inclusion or exclusion of specified fields. |
| ecommerce_update_store | Updates an e-commerce store with the specified parameters. |
| ecommerce_delete_store | Deletes an e-commerce store identified by the given store ID. |
| ecommerce_get_store_carts | Retrieves a list of carts from an e-commerce store with optional field filtering and pagination. |
| ecommerce_add_cart_to_store | Adds a shopping cart to the specified e-commerce store with customer, order, and line item details. |
| ecommerce_get_cart_info | Retrieves detailed information about a specific ecommerce cart from the specified store. |
| ecommerce_update_cart_by_id | Updates an existing e-commerce cart for a specified store and cart ID with new details such as customer info, campaign, checkout URL, currency, totals, and line items. |
| ecommerce_remove_cart | Removes a specific cart from an e-commerce store by cart ID. |
| ecommerce_list_cart_lines | Retrieves the list of line items from a specific e-commerce cart within a store. |
| ecommerce_add_cart_line_item | Adds a line item to an existing cart in the specified ecommerce store. |
| ecommerce_get_cart_line_item | Retrieves a specific cart line item from an e-commerce store by store, cart, and line identifiers, with optional field selection. |
| ecommerce_update_cart_line_item | Updates a specific line item in an e-commerce cart with new product details, quantity, or price. |
| ecommerce_delete_cart_line_item | Deletes a specific line item from a shopping cart in the specified store. |
| ecommerce_get_store_customers | Retrieves customers for a specified ecommerce store. |
| ecommerce_add_customer_to_store | Adds a customer to a specified e-commerce store. |
| ecommerce_get_customer_info | Retrieve detailed information about a specific customer in an e-commerce store. |
| ecommerce_add_or_update_customer | Adds a new e-commerce customer or updates an existing customer record for a specific store. |
| ecommerce_update_customer | Updates an existing customer's information in an e-commerce store. |
| ecommerce_remove_customer | Removes a customer from an e-commerce store |
| ecommerce_get_store_promo_rules | Retrieves a list of promotional rules for a specified e-commerce store, with optional filtering and pagination. |
| ecommerce_add_promo_rule | Creates and adds a new promotional rule to a specified ecommerce store. |
| ecommerce_get_store_promo_rule | Retrieves a specific promotional rule for an e-commerce store, optionally filtering the response fields. |
| ecommerce_update_promo_rule | Updates an existing promotional rule for an ecommerce store. |
| ecommerce_delete_promo_rule | Deletes a specific promotional rule from an e-commerce store. |
| ecommerce_get_store_promo_codes | Retrieves a list of promo codes associated with a specific promo rule for a store from the e-commerce API. |
| ecommerce_add_promo_code | Adds a promotional code to a specific promotion rule within an ecommerce store. |
| ecommerce_get_promo_code | Fetches a promo code for an ecommerce store using a specific promo rule and promo code ID. |
| ecommerce_update_promo_code | Updates an existing promo code for a specific store and promotion rule with the provided details. |
| ecommerce_delete_promo_code | Deletes a specific promotional code from an e-commerce store. |
| ecommerce_list_store_orders | Retrieves a list of orders for a specified e-commerce store, with optional filtering and field selection. |
| ecommerce_add_order_to_store | Adds a new order to the specified e-commerce store by submitting order and customer details to the backend API. |
| ecommerce_get_store_order_info | Retrieves information for a specific order from an e-commerce store. |
| ecommerce_update_specific_order | Updates details for a specific e-commerce order in the store, modifying only the provided fields. |
| ecommerce_delete_order | Deletes an order from an ecommerce store based on the provided store ID and order ID. |
| ecommerce_get_store_order_lines | Retrieves the order line items for a specific order in a store, with optional field selection and pagination. |
| ecommerce_add_order_line_item | Adds a line item to an existing order in the specified e-commerce store. |
| ecommerce_get_order_line_item | Retrieves a specific line item from an order in the specified ecommerce store. |
| ecommerce_update_order_line | Updates an existing order line in a store's e-commerce order with new product or pricing information. |
| ecommerce_delete_order_line | Deletes a specific line item from an order in the specified store via the e-commerce API. |
| ecommerce_get_store_products | Retrieves products from a specified ecommerce store |
| ecommerce_add_product_to_store | Adds a product to the specified e-commerce store with provided details and variants. |
| ecommerce_get_store_product_info | Retrieves detailed information about a specific product from an e-commerce store. |
| ecommerce_update_product | Updates an existing product in an e-commerce store with the provided details. |
| ecommerce_delete_product | Deletes a product from an e-commerce store by store and product ID. |
| ecommerce_list_product_variants | Retrieves a list of variants for a specified product in a given e-commerce store, with optional filtering and pagination. |
| ecommerce_add_product_variant | Adds a new product variant to the specified product in an ecommerce store. |
| ecommerce_get_product_variant_info | Retrieves detailed information about a specific product variant from an e-commerce store, with optional field selection. |
| ecommerce_add_or_update_product_variant | Adds a new product variant or updates an existing variant in the specified store's product catalog. |
| ecommerce_update_product_variant | Updates a product variant in the specified e-commerce store with provided attributes. |
| ecommerce_delete_product_variant | Deletes a specific product variant from an ecommerce store by issuing a DELETE request to the API. |
| ecommerce_get_product_images | Retrieves product images for a given store and product from an ecommerce API. |
| ecommerce_add_product_image | Adds an image to a product in the specified e-commerce store. |
| ecommerce_get_product_image_info | Retrieves detailed information about a specific product image from the e-commerce store, allowing optional filtering of returned fields. |
| ecommerce_update_product_image | Updates details of a product image in an ecommerce store using the provided identifiers and optional parameters. |
| ecommerce_delete_product_image | Deletes an image from a specified product in an e-commerce store. |
| search_campaigns_by_query_terms | Searches for campaigns matching the specified query terms and returns the results as a dictionary. |
| search_members_list_members | Searches for and retrieves a list of members matching the given query from a specific list, with optional field filtering. |
| ping_health_check | Checks the health status of the service by sending a ping request and returns the server's response as JSON. |
| facebook_ads_list_ads | Retrieves a list of Facebook ads with optional filtering, field selection, pagination, and sorting. |
| facebook_ads_get_info | Retrieves detailed information about a specific Facebook Ads outreach object using its ID, with optional field selection or exclusion. |
| reporting_list_facebook_ads_reports | Retrieves a list of Facebook Ads reports with optional filtering, pagination, and sorting. |
| reporting_facebook_ad_report | Retrieves detailed Facebook Ads reporting data for a specific outreach using the given outreach ID. |
| reporting_list_facebook_ecommerce_report | Retrieves a Facebook e-commerce product activity report for a specified outreach ID. |
| reporting_get_landing_page_report | Retrieves a landing page report for a specific outreach ID from the reporting API. |
| reporting_list_landing_pages_reports | Retrieves a list of landing pages reports with optional filtering, field selection, and pagination. |
| reporting_list_survey_reports | Retrieves a list of survey reports with optional filtering and pagination. |
| reporting_get_survey_report | Retrieves a survey report by its ID with optional field inclusions or exclusions. |
| reporting_list_survey_questions_reports | Fetches a list of survey question reports for a specified survey, with optional control over included or excluded fields. |
| reporting_survey_question_report | Retrieves a detailed report for a specific survey question, with optional field filtering. |
| reporting_survey_question_answers_list | Retrieves a list of answers for a specific survey question, with optional filtering and field selection. |
| reporting_survey_responses_list | Retrieves a list of survey response data for a specified survey, with optional filtering and field selection. |
| reporting_single_survey_response | Retrieves detailed information for a single survey response based on the provided survey and response identifiers. |
| verified_domains_get_info | Retrieves information about a verified domain by its domain name. |
| verified_domains_delete_domain | Deletes a verified domain by its domain name using a DELETE request to the API endpoint. |
| verified_domains_verify_domain_for_sending | Verifies a specified domain for sending capabilities using a provided verification code. |
| verified_domains_list_sending_domains | Retrieves a list of verified sending domains associated with the account. |
| verified_domains_add_domain_to_account | Adds a domain to the account for verification using the provided email address. |



## Usage

- Login to AgentR
- Follow the quickstart guide to setup MCP Server for your client
- Visit Apps Store and enable the Mailchimp app
- Restart the MCP Server

### Local Development

- Follow the README to test with the local MCP Server
