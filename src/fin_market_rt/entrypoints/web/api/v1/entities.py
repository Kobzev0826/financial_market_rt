from shop_settings_api.services.v1.entities import (
    ScriptsFilter,
    ShopGroup,
    ShopGroupInfo,
    ShopIdToApplyForToScript,
    ShopIdToBreadcrumbLimit,
    ShopIdToPromotionRules,
    ShopIdToRankingConfiguration,
    ShopIdToRulePartNameToShopRule,
    ShopIdToRules,
    ShopIdToShopFull,
    ShopIdToShopShort,
    ShopRules,
    ShopShort,
    ShopTagDefinition,
    UngroupedShop,
)

BreadcrumbLimitsResponse = ShopIdToBreadcrumbLimit
RankingConfigurationsResponse = ShopIdToRankingConfiguration
RulesResponse = ShopIdToRules
ShopRulesResponse = ShopIdToRulePartNameToShopRule
PromotionRulesResponse = ShopIdToPromotionRules
ScriptsFilterRequest = ScriptsFilter
ScriptsResponse = ShopIdToApplyForToScript
ShopShortResponse = ShopIdToShopShort
ShopShortListResponse = list[ShopShort]
ShopFullResponse = ShopIdToShopFull
GetShopRulesResponse = ShopRules
ShopTagsDefinitionsResponse = list[ShopTagDefinition]
ShopGroupsResponse = list[ShopGroup]
ShopGroupInfoResponse = ShopGroupInfo
UngroupedShopsResponse = list[UngroupedShop]
