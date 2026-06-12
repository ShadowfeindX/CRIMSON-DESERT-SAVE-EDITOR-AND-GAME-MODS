from __future__ import annotations

# from dataclasses import dataclass
from typing import List, TypedDict, Union

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

class CoolTimeData(TypedDict):
    """Represents cool time values for different character slots."""
    a: int
    """Cool time value for slot 'a'."""
    b: int
    """Cool time value for slot 'b'."""
    c: int
    """Cool time value for slot 'c'."""

class MaxedChargedUseableData(TypedDict):
    """Represents max charge values for different character slots."""
    a: int
    """Max charge value for slot 'a'."""
    b: int
    """Max charge value for slot 'b'."""
    c: int
    """Max charge value for slot 'c'."""


class ItemInfo(TypedDict):
    """A single item parsed from the iteminfo binary file."""

    # Identity
    key: int
    """Unique item ID. ItemKey (u32)."""
    string_key: str
    """String identifier, e.g. ``"Pyeonjeon_Arrow"``."""
    is_blocked: int
    """u8"""
    max_stack_count: int
    """u64"""
    item_name: LocalizableString
    broken_item_prefix_string: int
    """LocalStringInfoKey (u32)."""

    # Inventory & Equipment
    inventory_info: int
    """InventoryKey (u16)."""
    equip_type_info: int
    """EquipTypeKey (u32)."""
    occupied_equip_slot_data_list: list[OccupiedEquipSlotData]
    item_tag_list: list[int]
    """u32 list."""
    equipable_hash: int
    """u32"""
    consumable_type_list: list[int]
    """u32 list."""
    item_use_info_list: list[int]
    """ItemUseKey list (u32)."""
    item_icon_list: list[ItemIconData]
    map_icon_path: int
    """StringInfoKey (u32)."""
    money_icon_path: int
    """StringInfoKey (u32)."""
    use_map_icon_alert: int
    """u8"""
    item_type: int
    """u8"""
    material_key: int
    """u32"""
    material_match_info: int
    """MaterialMatchKey (u32)."""
    item_desc: LocalizableString
    item_desc2: LocalizableString
    equipable_level: int
    """u32"""
    category_info: int
    """CategoryKey (u16)."""
    knowledge_info: int
    """KnowledgeKey (u32)."""
    knowledge_obtain_type: int
    """u8"""
    destroy_effec_info: int
    """EffectKey (u32)."""
    equip_passive_skill_list: list[PassiveSkillLevel]
    use_immediately: int
    """u8"""
    apply_max_stack_cap: int
    """u8"""
    extract_multi_change_info: int
    """MultiChangeKey (u32)."""
    item_memo: str
    filter_type: str
    gimmick_info: int
    """GimmickInfoKey (u32)."""
    gimmick_tag_list: list[str]
    max_drop_result_sub_item_count: int
    """u32"""
    use_drop_set_target: int
    """u8"""
    is_all_gimmick_sealable: int
    """u8"""
    sealable_item_info_list: list[SealableItemInfo]
    sealable_character_info_list: list[SealableItemInfo]
    sealable_gimmick_info_list: list[SealableItemInfo]
    sealable_gimmick_tag_list: list[SealableItemInfo]
    sealable_tribe_info_list: list[SealableItemInfo]
    sealable_money_info_list: list[int]
    """ItemKey list (u32)."""
    delete_by_gimmick_unlock: int
    """u8"""
    gimmick_unlock_message_local_string_info: int
    """LocalStringInfoKey (u32)."""
    can_disassemble: int
    """u8"""
    transmutation_material_gimmick_list: list[int]
    """GimmickInfoKey list (u32)."""
    transmutation_material_item_list: list[int]
    """ItemKey list (u32)."""
    transmutation_material_group_list: list[int]
    """ItemGroupKey list (u16)."""
    is_register_trade_market: int
    """u8"""
    multi_change_info_list: list[int]
    """MultiChangeKey list (u32)."""
    is_editor_usable: int
    """u8"""
    discardable: int
    """u8"""
    is_dyeable: int
    """u8"""
    is_editable_grime: int
    """u8"""
    is_destroy_when_broken: int
    """u8"""
    quick_slot_index: int
    """u8"""
    reserve_slot_target_data_list: list[ReserveSlotTargetData]
    item_tier: int
    """u8"""
    is_important_item: int
    """u8"""
    apply_drop_stat_type: int
    """u8"""
    drop_default_data: DropDefaultData
    prefab_data_list: list[PrefabData]
    enchant_data_list: list[EnchantData]
    gimmick_visual_prefab_data_list: list[GimmickVisualPrefabData]
    price_list: list[ItemPriceInfo]
    docking_child_data: DockingChildData | None
    inventory_change_data: InventoryChangeData | None
    fixed_page_data_list: list[PageData]
    dynamic_page_data_list: list[PageData]
    inspect_data_list: list[InspectData]
    inspect_action: InspectAction
    default_sub_item: SubItem
    cooltime: CoolTimeData # ADDED PROPERTY
    discard_attach_terrain: int # ADDED PROPERTY
    item_charge_type: int
    """u8"""
    sharpness_data: ItemInfoSharpnessData
    max_charged_useable_count: MaxedChargedUseableData
    hackable_character_group_info_list: list[int]
    """CharacterGroupKey list (u16)."""
    item_group_info_list: list[int]
    """ItemGroupKey list (u16)."""
    discard_offset_y: float
    """f32"""
    hide_from_inventory_on_pop_item: int
    """u8"""
    is_shield_item: int
    """u8"""
    is_tower_shield_item: int
    """u8"""
    is_wild: int
    """u8"""
    packed_item_info: int
    """ItemKey (u32)."""
    unpacked_item_info: int
    """ItemKey (u32)."""
    convert_item_info_by_drop_npc: int
    """ItemKey (u32)."""
    look_detail_game_advice_info_wrapper: int
    """GameAdviceInfoKey (u32)."""
    look_detail_mission_info: int
    """MissionKey (u32)."""
    enable_alert_system_to_ui: int
    """u8"""
    usable_alert_type: int
    """u8"""
    is_save_game_data_at_use_item: int
    """u8"""
    is_logout_at_use_item: int
    """u8"""
    shared_cool_time_group_name_hash: int
    """u32"""
    item_bundle_data_list: list[ItemBundleData]
    money_type_define: MoneyTypeDefine | None
    emoji_texture_id: str
    enable_equip_in_clone_actor: int
    """u8"""
    is_blocked_store_sell: int
    """u8"""
    is_preorder_item: int
    """u8"""
    respawn_time_seconds: int
    """i64"""
    max_endurance: int
    """u16"""
    repair_data_list: list[RepairData]

class UpgradeGraph(TypedDict):
    a: int
    b: int
    c: int
    d: int

class ResourceItem(TypedDict):
    lookup: int
    value: int

class BuffBase(TypedDict):
    asset_path: str
    by132: int
    by58: int
    by68: int
    by69: int
    carray_u16: List[int]
    carray_u32: List[int]
    category: int
    flags_a: int
    flags_b: int
    id: int
    lookup_88: int
    lookup_90: int
    lookup_a_60: int
    lookup_b_62: int
    lookup_c_64: int
    lookup_d_66: int
    name_id: int
    qword_a: int
    qword_b: int
    qword_c: int
    tag: int
    u32_at128: int
    u32_at136: int
    u32_at72: int
    u32_at76: int
    u32_at80: int
    u32_at84: int

class BuffVariantBody(TypedDict, total=False):
    f00: Union[int, List[int]]
    f01: int
    f02: int
    f03: int
    f04: int

class BuffVariant(TypedDict):
    body: BuffVariantBody
    type: str

class BuffEntry(TypedDict):
    absent_flag: int
    base: BuffBase
    variant: BuffVariant

class SkillInfo(TypedDict):
    """A single item parsed from the skillinfo binary file."""

    allow_skill_with_low_resource: int
    apply_type: int
    buff_level_list: List[List[BuffEntry]]
    buff_sustain_flag: int
    cooltime: int
    damage_type: int
    dev_extra_a: str
    dev_extra_b: str
    dev_skill_desc: str
    dev_skill_name: str
    faction_info: int
    icon_path: int
    is_blocked: int
    is_learn_use_artifact: int
    is_ui_use_allowed: int
    is_use_child_pattern_description_buff_data: int
    key: int
    learn_knowledge_info: int
    learn_level: int
    max_level: int
    need_upgrade_experience_graph: UpgradeGraph
    need_upgrade_item_count_graph: UpgradeGraph
    need_upgrade_item_info: int
    parent_skill: int
    reserve_slot_info_list: List
    skill_group_key: int
    skill_group_key_list: List[int]
    string_key: str
    ui_type: int
    usable_character_info_list: List
    usable_condition: List[int]
    use_battery_stat: int
    use_driver_resource_stat_list: List
    use_resource_item_list: List[ResourceItem]
    use_resource_stat_list: List
    video_path: int

def _safe_iv(v, default=0):
    """Safely extract int from plain int, float, or dmm_parser nested dict.
    dmm_parser returns numeric structs as {'a': int, 'b': int, 'c': int}.
    """
    if v is None:
        return default
    if isinstance(v, (int, float, bool)):
        return int(v)
    if isinstance(v, dict):
        for k in ("a", "value", "_v", "v", "val", "n", "data"):
            if k in v:
                sub = v[k]
                if isinstance(sub, (int, float, bool)):
                    return int(sub)
                if sub is None:
                    return default
        return default
    try:
        return int(v)
    except Exception:
        return default