r'''
# `tfe_vault_oidc_configuration`

Refer to the Terraform Registry for docs: [`tfe_vault_oidc_configuration`](https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/vault_oidc_configuration).
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from .._jsii import *

import cdktf as _cdktf_9a9027ec
import constructs as _constructs_77d1e7e8


class VaultOidcConfiguration(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-tfe.vaultOidcConfiguration.VaultOidcConfiguration",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/vault_oidc_configuration tfe_vault_oidc_configuration}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        address: builtins.str,
        namespace: builtins.str,
        role_name: builtins.str,
        auth_path: typing.Optional[builtins.str] = None,
        encoded_cacert: typing.Optional[builtins.str] = None,
        organization: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/vault_oidc_configuration tfe_vault_oidc_configuration} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param address: The full address of your Vault instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/vault_oidc_configuration#address VaultOidcConfiguration#address}
        :param namespace: The namespace your JWT auth path is mounted in. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/vault_oidc_configuration#namespace VaultOidcConfiguration#namespace}
        :param role_name: The name of a role in your Vault JWT auth path, with permission to encrypt and decrypt with a Transit secrets engine key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/vault_oidc_configuration#role_name VaultOidcConfiguration#role_name}
        :param auth_path: The mounting path of JWT auth path of JWT auth. Defaults to "jwt". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/vault_oidc_configuration#auth_path VaultOidcConfiguration#auth_path}
        :param encoded_cacert: A base64 encoded certificate which can be used to authenticate your Vault certificate. Only needed for self-hosted Vault Enterprise instances with a self-signed certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/vault_oidc_configuration#encoded_cacert VaultOidcConfiguration#encoded_cacert}
        :param organization: Name of the organization to which the TFE Vault OIDC configuration belongs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/vault_oidc_configuration#organization VaultOidcConfiguration#organization}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__378f32fef31ea990a8c5226d6c0beb422908fafd355b30249824ab7da06eccf1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = VaultOidcConfigurationConfig(
            address=address,
            namespace=namespace,
            role_name=role_name,
            auth_path=auth_path,
            encoded_cacert=encoded_cacert,
            organization=organization,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a VaultOidcConfiguration resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the VaultOidcConfiguration to import.
        :param import_from_id: The id of the existing VaultOidcConfiguration that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/vault_oidc_configuration#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the VaultOidcConfiguration to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdc6040eecf5745a61ee14deca441290c7300f4b176ecd8a112f07c44ee01fc0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAuthPath")
    def reset_auth_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthPath", []))

    @jsii.member(jsii_name="resetEncodedCacert")
    def reset_encoded_cacert(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncodedCacert", []))

    @jsii.member(jsii_name="resetOrganization")
    def reset_organization(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrganization", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="synthesizeHclAttributes")
    def _synthesize_hcl_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeHclAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="addressInput")
    def address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "addressInput"))

    @builtins.property
    @jsii.member(jsii_name="authPathInput")
    def auth_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authPathInput"))

    @builtins.property
    @jsii.member(jsii_name="encodedCacertInput")
    def encoded_cacert_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encodedCacertInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="organizationInput")
    def organization_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "organizationInput"))

    @builtins.property
    @jsii.member(jsii_name="roleNameInput")
    def role_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleNameInput"))

    @builtins.property
    @jsii.member(jsii_name="address")
    def address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "address"))

    @address.setter
    def address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24a0bb2e03a64d97f348696824b506e1a699101689427e9ba6ee3593d5d5c8d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "address", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="authPath")
    def auth_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authPath"))

    @auth_path.setter
    def auth_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9c4214a411d11df8de5baf439bbdd6af77b45c7e63772a48d8b6db4980ca458)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authPath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="encodedCacert")
    def encoded_cacert(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encodedCacert"))

    @encoded_cacert.setter
    def encoded_cacert(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__015e8b39a055d75c4fd7633963711c01a581b58ae5866ed9266fcd2495253fe1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "encodedCacert", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec69839a59db4b48553c818805205ee7ab9c010e2ab342eb4263506f7ddd16b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="organization")
    def organization(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "organization"))

    @organization.setter
    def organization(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4042c4e8ec1e76dfa8300ec9d43f032b9520257644bab8b4a97cf7ce084c87c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "organization", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="roleName")
    def role_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleName"))

    @role_name.setter
    def role_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52a32e0705c9ba75c0dd9b19b3902369bc0a8d32d6b0b5d83578e88214c39e1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "roleName", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-tfe.vaultOidcConfiguration.VaultOidcConfigurationConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "address": "address",
        "namespace": "namespace",
        "role_name": "roleName",
        "auth_path": "authPath",
        "encoded_cacert": "encodedCacert",
        "organization": "organization",
    },
)
class VaultOidcConfigurationConfig(_cdktf_9a9027ec.TerraformMetaArguments):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
        address: builtins.str,
        namespace: builtins.str,
        role_name: builtins.str,
        auth_path: typing.Optional[builtins.str] = None,
        encoded_cacert: typing.Optional[builtins.str] = None,
        organization: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param address: The full address of your Vault instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/vault_oidc_configuration#address VaultOidcConfiguration#address}
        :param namespace: The namespace your JWT auth path is mounted in. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/vault_oidc_configuration#namespace VaultOidcConfiguration#namespace}
        :param role_name: The name of a role in your Vault JWT auth path, with permission to encrypt and decrypt with a Transit secrets engine key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/vault_oidc_configuration#role_name VaultOidcConfiguration#role_name}
        :param auth_path: The mounting path of JWT auth path of JWT auth. Defaults to "jwt". Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/vault_oidc_configuration#auth_path VaultOidcConfiguration#auth_path}
        :param encoded_cacert: A base64 encoded certificate which can be used to authenticate your Vault certificate. Only needed for self-hosted Vault Enterprise instances with a self-signed certificate. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/vault_oidc_configuration#encoded_cacert VaultOidcConfiguration#encoded_cacert}
        :param organization: Name of the organization to which the TFE Vault OIDC configuration belongs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/vault_oidc_configuration#organization VaultOidcConfiguration#organization}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5154fec55ae898b57a11f4ff7f4d7fa4586d6263fdad5e4de0d04d283248065)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument address", value=address, expected_type=type_hints["address"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument role_name", value=role_name, expected_type=type_hints["role_name"])
            check_type(argname="argument auth_path", value=auth_path, expected_type=type_hints["auth_path"])
            check_type(argname="argument encoded_cacert", value=encoded_cacert, expected_type=type_hints["encoded_cacert"])
            check_type(argname="argument organization", value=organization, expected_type=type_hints["organization"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "address": address,
            "namespace": namespace,
            "role_name": role_name,
        }
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners
        if auth_path is not None:
            self._values["auth_path"] = auth_path
        if encoded_cacert is not None:
            self._values["encoded_cacert"] = encoded_cacert
        if organization is not None:
            self._values["organization"] = organization

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]], result)

    @builtins.property
    def count(
        self,
    ) -> typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]], result)

    @builtins.property
    def depends_on(
        self,
    ) -> typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[_cdktf_9a9027ec.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[_cdktf_9a9027ec.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]], result)

    @builtins.property
    def address(self) -> builtins.str:
        '''The full address of your Vault instance.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/vault_oidc_configuration#address VaultOidcConfiguration#address}
        '''
        result = self._values.get("address")
        assert result is not None, "Required property 'address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def namespace(self) -> builtins.str:
        '''The namespace your JWT auth path is mounted in.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/vault_oidc_configuration#namespace VaultOidcConfiguration#namespace}
        '''
        result = self._values.get("namespace")
        assert result is not None, "Required property 'namespace' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_name(self) -> builtins.str:
        '''The name of a role in your Vault JWT auth path, with permission to encrypt and decrypt with a Transit secrets engine key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/vault_oidc_configuration#role_name VaultOidcConfiguration#role_name}
        '''
        result = self._values.get("role_name")
        assert result is not None, "Required property 'role_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auth_path(self) -> typing.Optional[builtins.str]:
        '''The mounting path of JWT auth path of JWT auth. Defaults to "jwt".

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/vault_oidc_configuration#auth_path VaultOidcConfiguration#auth_path}
        '''
        result = self._values.get("auth_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encoded_cacert(self) -> typing.Optional[builtins.str]:
        '''A base64 encoded certificate which can be used to authenticate your Vault certificate.

        Only needed for self-hosted Vault Enterprise instances with a self-signed certificate.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/vault_oidc_configuration#encoded_cacert VaultOidcConfiguration#encoded_cacert}
        '''
        result = self._values.get("encoded_cacert")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def organization(self) -> typing.Optional[builtins.str]:
        '''Name of the organization to which the TFE Vault OIDC configuration belongs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/tfe/0.71.0/docs/resources/vault_oidc_configuration#organization VaultOidcConfiguration#organization}
        '''
        result = self._values.get("organization")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VaultOidcConfigurationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "VaultOidcConfiguration",
    "VaultOidcConfigurationConfig",
]

publication.publish()

def _typecheckingstub__378f32fef31ea990a8c5226d6c0beb422908fafd355b30249824ab7da06eccf1(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    address: builtins.str,
    namespace: builtins.str,
    role_name: builtins.str,
    auth_path: typing.Optional[builtins.str] = None,
    encoded_cacert: typing.Optional[builtins.str] = None,
    organization: typing.Optional[builtins.str] = None,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdc6040eecf5745a61ee14deca441290c7300f4b176ecd8a112f07c44ee01fc0(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24a0bb2e03a64d97f348696824b506e1a699101689427e9ba6ee3593d5d5c8d1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9c4214a411d11df8de5baf439bbdd6af77b45c7e63772a48d8b6db4980ca458(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__015e8b39a055d75c4fd7633963711c01a581b58ae5866ed9266fcd2495253fe1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec69839a59db4b48553c818805205ee7ab9c010e2ab342eb4263506f7ddd16b3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4042c4e8ec1e76dfa8300ec9d43f032b9520257644bab8b4a97cf7ce084c87c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52a32e0705c9ba75c0dd9b19b3902369bc0a8d32d6b0b5d83578e88214c39e1c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5154fec55ae898b57a11f4ff7f4d7fa4586d6263fdad5e4de0d04d283248065(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    address: builtins.str,
    namespace: builtins.str,
    role_name: builtins.str,
    auth_path: typing.Optional[builtins.str] = None,
    encoded_cacert: typing.Optional[builtins.str] = None,
    organization: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
