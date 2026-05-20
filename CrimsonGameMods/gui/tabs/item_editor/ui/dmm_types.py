from __future__ import annotations

from typing import TypedDict

class LocalizableString(TypedDict):
    category: int
    """Localization category (u8)."""
    index: int
    """Localization table index (u64)."""
    default: str
    """Default string value."""


class OccupiedEquipSlotData(TypedDict):
    equip_slot_name_key: int
    """u32"""
    equip_slot_name_index_list: list[int]
    """list of u8 values."""


class ItemIconData(TypedDict):
    icon_path: int
    """StringInfoKey (u32)."""
    check_exist_sealed_data: int
    """u8"""
    gimmick_state_list: list[int]
    """list of u32."""


class PassiveSkillLevel(TypedDict):
    skill: int
    """SkillKey (u32)."""
    level: int
    """u32"""


class ReserveSlotTargetData(TypedDict):
    reserve_slot_info: int
    """ReserveSlotKey (u32)."""
    condition_info: int
    """ConditionKey (u32)."""


class SocketMaterialItem(TypedDict):
    item: int
    """ItemKey (u32)."""
    value: int
    """u64"""


class EnchantStatChange(TypedDict):
    stat: int
    """StatusKey (u32)."""
    change_mb: int
    """i64"""


class EnchantLevelChange(TypedDict):
    stat: int
    """StatusKey (u32)."""
    change_mb: int
    """i8"""


class EnchantStatData(TypedDict):
    max_stat_list: list[EnchantStatChange]
    regen_stat_list: list[EnchantStatChange]
    stat_list_static: list[EnchantStatChange]
    stat_list_static_level: list[EnchantLevelChange]


class PriceFloor(TypedDict):
    price: int
    """u64"""
    sym_no: int
    """u32"""
    item_info_wrapper: int
    """ItemKey (u32)."""


class ItemPriceInfo(TypedDict):
    key: int
    """ItemKey (u32)."""
    price: PriceFloor


class EquipmentBuff(TypedDict):
    buff: int
    """BuffKey (u32)."""
    level: int
    """u32"""


class EnchantData(TypedDict):
    level: int
    """u16"""
    enchant_stat_data: EnchantStatData
    buy_price_list: list[ItemPriceInfo]
    equip_buffs: list[EquipmentBuff]


class GimmickVisualPrefabData(TypedDict):
    tag_name_hash: int
    """u32"""
    scale: list[float]
    """[f32; 3] - 3 floats."""
    prefab_names: list[int]
    """StringInfoKey list (u32)."""
    animation_path_list: list[int]
    """StringInfoKey list (u32)."""
    use_gimmick_prefab: int
    """u8"""


class GameEventExecuteData(TypedDict):
    game_event_type: int
    """u8"""
    player_condition: int
    """ConditionKey (u32)."""
    target_condition: int
    """ConditionKey (u32)."""
    event_condition: int
    """ConditionKey (u32)."""


class InventoryChangeData(TypedDict):
    game_event_execute_data: GameEventExecuteData
    to_inventory_info: int
    """InventoryKey (u16)."""


class PageData(TypedDict):
    left_page_texture_path: str
    right_page_texture_path: str
    left_page_related_knowledge_info: int
    """KnowledgeKey (u32)."""
    right_page_related_knowledge_info: int
    """KnowledgeKey (u32)."""


class InspectData(TypedDict):
    item_info: int
    """ItemKey (u32)."""
    gimmick_info: int
    """GimmickInfoKey (u32)."""
    character_info: int
    """CharacterKey (u32)."""
    spawn_reason_hash: int
    """u32"""
    socket_name: str
    speak_character_info: int
    """CharacterKey (u32)."""
    inspect_target_tag: int
    """u32"""
    reward_own_knowledge: int
    """u8"""
    reward_knowledge_info: int
    """KnowledgeKey (u32)."""
    item_desc: LocalizableString
    board_key: int
    """u32"""
    inspect_action_type: int
    """u8"""
    gimmick_state_name_hash: int
    """u32"""
    target_page_index: int
    """u32"""
    is_left_page: int
    """u8"""
    target_page_related_knowledge_info: int
    """KnowledgeKey (u32)."""
    enable_read_after_reward: int
    """u8"""
    refer_to_left_page_inspect_data: int
    """u8"""
    inspect_effect_info_key: int
    """EffectKey (u32)."""
    inspect_complete_effect_info_key: int
    """EffectKey (u32)."""


class InspectAction(TypedDict):
    action_name_hash: int
    """u32"""
    catch_tag_name_hash: int
    """u32"""
    catcher_socket_name: str
    catch_target_socket_name: str


class ItemInfoSharpnessData(TypedDict):
    max_sharpness: int
    """u16"""
    craft_tool_info: int
    """CraftToolKey (u16)."""
    stat_data: EnchantStatData


class ItemBundleData(TypedDict):
    count_mb: int
    """u64"""
    key: int
    """GimmickInfoKey (u32)."""


class UnitData(TypedDict):
    ui_component: str
    minimum: int
    """u32"""
    icon_path: int
    """StringInfoKey (u32)."""
    item_name: LocalizableString
    item_desc: LocalizableString


class MoneyUnitEntry(TypedDict):
    key: int
    """u32"""
    value: UnitData


class MoneyTypeDefine(TypedDict):
    price_floor_value: int
    """u64"""
    unit_data_list_map: list[MoneyUnitEntry]


class PrefabData(TypedDict):
    prefab_names: list[int]
    """StringInfoKey list (u32)."""
    equip_slot_list: list[int]
    """u16 list."""
    tribe_gender_list: list[int]
    """StringInfoKey list (u32)."""
    is_craft_material: int
    """u8"""


class RepairData(TypedDict):
    resource_item_info: int
    """ItemKey (u32)."""
    repair_value: int
    """u16"""
    repair_style: int
    """u8"""
    resource_item_count: int
    """u64"""


class SubItem(TypedDict):
    type_id: int
    """u8 variant tag. 0=Item, 3=Character, 9=Gimmick, 14=None."""
    value: int | None
    """Key value (u32) or None for type_id=14."""


class DropDefaultData(TypedDict):
    drop_enchant_level: int
    """u16"""
    socket_item_list: list[int]
    """ItemKey list (u32)."""
    add_socket_material_item_list: list[SocketMaterialItem]
    default_sub_item: SubItem
    socket_valid_count: int
    """u8"""
    use_socket: int
    """u8"""


class SealableItemInfo(TypedDict):
    type_tag: int
    """u8 variant tag. 0=Item, 1=Gimmick, 2=String, 3=Character, 4=Tribe."""
    item_key: int
    """ItemKey (u32)."""
    unknown0: int
    """u64"""
    value: int | str
    """Key value (u32) for types 0/1/3/4, or str for type 2."""


class DockingChildData(TypedDict):
    gimmick_info_key: int
    """GimmickInfoKey (u32)."""
    character_key: int
    """CharacterKey (u32)."""
    item_key: int
    """ItemKey (u32)."""
    attach_parent_socket_name: str
    attach_child_socket_name: str
    docking_tag_name_hash: list[int]
    """[u32; 4] - 4 ints."""
    docking_equip_slot_no: int
    """u16"""
    spawn_distance_level: int
    """u32"""
    is_item_equip_docking_gimmick: int
    """u8"""
    send_damage_to_parent: int
    """u8"""
    is_body_part: int
    """u8"""
    docking_type: int
    """u8"""
    is_summoner_team: int
    """u8"""
    is_player_only: int
    """u8"""
    is_npc_only: int
    """ConditionKey (u32)."""
    is_sync_break_parent: int
    """u8"""
    hit_part: int
    """u8"""
    detected_by_npc: int
    """u8"""
    is_bag_docking: int
    """u8"""
    enable_collision: int
    """u8"""
    disable_collision_with_other_gimmick: int
    """u8"""
    docking_slot_key: str


class ItemInfo(TypedDict):
    """A single item parsed from the iteminfo binary file."""

    # Identity
    _key: int
    """Unique item ID. ItemKey (u32)."""
    _stringKey: str
    """String identifier, e.g. ``"Pyeonjeon_Arrow"``."""
    _isBlocked: int
    """u8"""
    _maxStackCount: int
    """u64"""
    _itemName: LocalizableString
    _brokenItemPrefixString: int
    """LocalStringInfoKey (u32)."""

    # Inventory & Equipment
    _inventoryInfo: int
    """InventoryKey (u16)."""
    _equipTypeInfo: int
    """EquipTypeKey (u32)."""
    _occupiedEquipSlotDataList: list[OccupiedEquipSlotData]
    _itemTagList: list[int]
    """u32 list."""
    _equipableHash: int
    """u32"""
    _consumableTypeList: list[int]
    """u32 list."""
    _itemUseInfoList: list[int]
    """ItemUseKey list (u32)."""
    _itemIconList: list[ItemIconData]
    _mapIconPath: int
    """StringInfoKey (u32)."""
    _moneyIconPath: int
    """StringInfoKey (u32)."""
    _useMapIconAlert: int
    """u8"""
    _itemType: int
    """u8"""
    _materialKey: int
    """u32"""
    _materialMatchInfo: int
    """MaterialMatchKey (u32)."""
    _itemDesc: LocalizableString
    _itemDesc2: LocalizableString
    _equipableLevel: int
    """u32"""
    _categoryInfo: int
    """CategoryKey (u16)."""
    _knowledgeInfo: int
    """KnowledgeKey (u32)."""
    _knowledgeObtainType: int
    """u8"""
    _destroyEffecInfo: int
    """EffectKey (u32)."""
    _equipPassiveSkillList: list[PassiveSkillLevel]
    _useImmediately: int
    """u8"""
    _applyMaxStackCap: int
    """u8"""
    _extractMultiChangeInfo: int
    """MultiChangeKey (u32)."""
    _itemMemo: str
    _filterType: str
    _gimmickInfo: int
    """GimmickInfoKey (u32)."""
    _gimmickTagList: list[str]
    _maxDropResultSubItemCount: int
    """u32"""
    _useDropSetTarget: int
    """u8"""
    _isAllGimmickSealable: int
    """u8"""
    _sealableItemInfoList: list[SealableItemInfo]
    _sealableCharacterInfoList: list[SealableItemInfo]
    _sealableGimmickInfoList: list[SealableItemInfo]
    _sealableGimmickTagList: list[SealableItemInfo]
    _sealableTribeInfoList: list[SealableItemInfo]
    _sealableMoneyInfoList: list[int]
    """ItemKey list (u32)."""
    _deleteByGimmickUnlock: int
    """u8"""
    _gimmickUnlockMessageLocalStringInfo: int
    """LocalStringInfoKey (u32)."""
    _canDisassemble: int
    """u8"""
    _transmutationMaterialGimmickList: list[int]
    """GimmickInfoKey list (u32)."""
    _transmutationMaterialItemList: list[int]
    """ItemKey list (u32)."""
    _transmutationMaterialItemGroupList: list[int]
    """ItemGroupKey list (u16)."""
    _isRegisterTradeMarket: int
    """u8"""
    _multiChangeInfoList: list[int]
    """MultiChangeKey list (u32)."""
    _isEditorUsable: int
    """u8"""
    _discardable: int
    """u8"""
    _isDyeable: int
    """u8"""
    _isEditableGrime: int
    """u8"""
    _isDestroyWhenBroken: int
    """u8"""
    _quickSlotIndex: int
    """u8"""
    _reserveSlotTargetDataList: list[ReserveSlotTargetData]
    _itemTier: int
    """u8"""
    _isImportantItem: int
    """u8"""
    _applyDropStatType: int
    """u8"""
    _dropDefaultData: DropDefaultData
    _prefabDataList: list[PrefabData]
    _enchantDataList: list[EnchantData]
    _gimmickVisualPrefabDataList: list[GimmickVisualPrefabData]
    _priceList: list[ItemPriceInfo]
    _dockingChildData: DockingChildData | None
    _inventoryChangeData: InventoryChangeData | None
    _fixedPageDataList: list[PageData]
    _dynamicPageDataList: list[PageData]
    _inspectDataList: list[InspectData]
    _inspectAction: InspectAction
    _defaultSubItem: SubItem
    _cooltime: int
    """i64"""
    _itemChargeType: int
    """u8"""
    _sharpnessData: ItemInfoSharpnessData
    _maxChargedUseableCount: int
    """u32"""
    _hackableCharacterGroupInfoList: list[int]
    """CharacterGroupKey list (u16)."""
    _itemGroupInfoList: list[int]
    """ItemGroupKey list (u16)."""
    _discardOffsetY: float
    """f32"""
    _hideFromInventoryOnPopItem: int
    """u8"""
    _isShieldItem: int
    """u8"""
    _isTowerShieldItem: int
    """u8"""
    _isWild: int
    """u8"""
    _packedItemInfo: int
    """ItemKey (u32)."""
    _unpackedItemInfo: int
    """ItemKey (u32)."""
    _convertItemInfoByDropNpc: int
    """ItemKey (u32)."""
    _lookDetailGameAdviceInfoWrapper: int
    """GameAdviceInfoKey (u32)."""
    _lookDetailMissionInfo: int
    """MissionKey (u32)."""
    _enableAlertSystemToUi: int
    """u8"""
    _usableAlertType: int
    """u8"""
    _isSaveGameDataAtUseItem: int
    """u8"""
    _isLogoutAtUseItem: int
    """u8"""
    _sharedCoolTimeGroupNameHash: int
    """u32"""
    _itemBundleDataList: list[ItemBundleData]
    _moneyTypeDefine: MoneyTypeDefine | None
    _emojiTextureId: str
    _enableEquipInCloneActor: int
    """u8"""
    _isBlockedStoreSell: int
    """u8"""
    _isPreorderItem: int
    """u8"""
    _respawnTimeSeconds: int
    """i64"""
    _maxEndurance: int
    """u16"""
    _repairDataList: list[RepairData]