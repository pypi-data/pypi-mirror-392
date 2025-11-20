# coding: utf-8

"""
    API REST FactPulse

     API REST pour la facturation électronique en France : Factur-X, AFNOR PDP/PA, signatures électroniques.  ## 🎯 Fonctionnalités principales  ### 📄 Génération de factures Factur-X - **Formats** : XML seul ou PDF/A-3 avec XML embarqué - **Profils** : MINIMUM, BASIC, EN16931, EXTENDED - **Normes** : EN 16931 (directive UE 2014/55), ISO 19005-3 (PDF/A-3), CII (UN/CEFACT) - **🆕 Format simplifié** : Génération à partir de SIRET + auto-enrichissement (API Chorus Pro + Recherche Entreprises)  ### ✅ Validation et conformité - **Validation XML** : Schematron (45 à 210+ règles selon profil) - **Validation PDF** : PDF/A-3, métadonnées XMP Factur-X, signatures électroniques - **VeraPDF** : Validation stricte PDF/A (146+ règles ISO 19005-3) - **Traitement asynchrone** : Support Celery pour validations lourdes (VeraPDF)  ### 📡 Intégration AFNOR PDP/PA (XP Z12-013) - **Soumission de flux** : Envoi de factures vers Plateformes de Dématérialisation Partenaires - **Recherche de flux** : Consultation des factures soumises - **Téléchargement** : Récupération des PDF/A-3 avec XML - **Directory Service** : Recherche d'entreprises (SIREN/SIRET) - **Multi-client** : Support de plusieurs configs PDP par utilisateur (stored credentials ou zero-storage)  ### ✍️ Signature électronique PDF - **Standards** : PAdES-B-B, PAdES-B-T (horodatage RFC 3161), PAdES-B-LT (archivage long terme) - **Niveaux eIDAS** : SES (auto-signé), AdES (CA commerciale), QES (PSCO) - **Validation** : Vérification intégrité cryptographique et certificats - **Génération de certificats** : Certificats X.509 auto-signés pour tests  ### 🔄 Traitement asynchrone - **Celery** : Génération, validation et signature asynchrones - **Polling** : Suivi d'état via `/taches/{id_tache}/statut` - **Pas de timeout** : Idéal pour gros fichiers ou validations lourdes  ## 🔒 Authentification  Toutes les requêtes nécessitent un **token JWT** dans le header Authorization : ``` Authorization: Bearer YOUR_JWT_TOKEN ```  ### Comment obtenir un token JWT ?  #### 🔑 Méthode 1 : API `/api/token/` (Recommandée)  **URL :** `https://www.factpulse.fr/api/token/`  Cette méthode est **recommandée** pour l'intégration dans vos applications et workflows CI/CD.  **Prérequis :** Avoir défini un mot de passe sur votre compte  **Pour les utilisateurs inscrits via email/password :** - Vous avez déjà un mot de passe, utilisez-le directement  **Pour les utilisateurs inscrits via OAuth (Google/GitHub) :** - Vous devez d'abord définir un mot de passe sur : https://www.factpulse.fr/accounts/password/set/ - Une fois le mot de passe créé, vous pourrez utiliser l'API  **Exemple de requête :** ```bash curl -X POST https://www.factpulse.fr/api/token/ \\   -H \"Content-Type: application/json\" \\   -d '{     \"username\": \"votre_email@example.com\",     \"password\": \"votre_mot_de_passe\"   }' ```  **Paramètre optionnel `client_uid` :**  Pour sélectionner les credentials d'un client spécifique (PA/PDP, Chorus Pro, certificats de signature), ajoutez `client_uid` :  ```bash curl -X POST https://www.factpulse.fr/api/token/ \\   -H \"Content-Type: application/json\" \\   -d '{     \"username\": \"votre_email@example.com\",     \"password\": \"votre_mot_de_passe\",     \"client_uid\": \"550e8400-e29b-41d4-a716-446655440000\"   }' ```  Le `client_uid` sera inclus dans le JWT et permettra à l'API d'utiliser automatiquement : - Les credentials AFNOR/PDP configurés pour ce client - Les credentials Chorus Pro configurés pour ce client - Les certificats de signature électronique configurés pour ce client  **Réponse :** ```json {   \"access\": \"eyJ0eXAiOiJKV1QiLCJhbGc...\",  // Token d'accès (validité: 30 min)   \"refresh\": \"eyJ0eXAiOiJKV1QiLCJhbGc...\"  // Token de rafraîchissement (validité: 7 jours) } ```  **Avantages :** - ✅ Automatisation complète (CI/CD, scripts) - ✅ Gestion programmatique des tokens - ✅ Support du refresh token pour renouveler automatiquement l'accès - ✅ Intégration facile dans n'importe quel langage/outil  #### 🖥️ Méthode 2 : Génération via Dashboard (Alternative)  **URL :** https://www.factpulse.fr/dashboard/  Cette méthode convient pour des tests rapides ou une utilisation occasionnelle via l'interface graphique.  **Fonctionnement :** - Connectez-vous au dashboard - Utilisez les boutons \"Generate Test Token\" ou \"Generate Production Token\" - Fonctionne pour **tous** les utilisateurs (OAuth et email/password), sans nécessiter de mot de passe  **Types de tokens :** - **Token Test** : Validité 24h, quota 1000 appels/jour (gratuit) - **Token Production** : Validité 7 jours, quota selon votre forfait  **Avantages :** - ✅ Rapide pour tester l'API - ✅ Aucun mot de passe requis - ✅ Interface visuelle simple  **Inconvénients :** - ❌ Nécessite une action manuelle - ❌ Pas de refresh token - ❌ Moins adapté pour l'automatisation  ### 📚 Documentation complète  Pour plus d'informations sur l'authentification et l'utilisation de l'API : https://www.factpulse.fr/documentation-api/     

    The version of the OpenAPI document: 1.0.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501

import warnings
from pydantic import validate_call, Field, StrictFloat, StrictStr, StrictInt
from typing import Any, Dict, List, Optional, Tuple, Union
from typing_extensions import Annotated

from pydantic import StrictInt
from typing import Any
from factpulse.models.body_ajouter_fichier_api_v1_chorus_pro_transverses_ajouter_fichier_post import BodyAjouterFichierApiV1ChorusProTransversesAjouterFichierPost
from factpulse.models.body_completer_facture_api_v1_chorus_pro_factures_completer_post import BodyCompleterFactureApiV1ChorusProFacturesCompleterPost
from factpulse.models.body_lister_services_structure_api_v1_chorus_pro_structures_id_structure_cpp_services_get import BodyListerServicesStructureApiV1ChorusProStructuresIdStructureCppServicesGet
from factpulse.models.body_rechercher_factures_destinataire_api_v1_chorus_pro_factures_rechercher_destinataire_post import BodyRechercherFacturesDestinataireApiV1ChorusProFacturesRechercherDestinatairePost
from factpulse.models.body_rechercher_factures_fournisseur_api_v1_chorus_pro_factures_rechercher_fournisseur_post import BodyRechercherFacturesFournisseurApiV1ChorusProFacturesRechercherFournisseurPost
from factpulse.models.body_recycler_facture_api_v1_chorus_pro_factures_recycler_post import BodyRecyclerFactureApiV1ChorusProFacturesRecyclerPost
from factpulse.models.body_telecharger_groupe_factures_api_v1_chorus_pro_factures_telecharger_groupe_post import BodyTelechargerGroupeFacturesApiV1ChorusProFacturesTelechargerGroupePost
from factpulse.models.body_traiter_facture_recue_api_v1_chorus_pro_factures_traiter_facture_recue_post import BodyTraiterFactureRecueApiV1ChorusProFacturesTraiterFactureRecuePost
from factpulse.models.body_valideur_consulter_facture_api_v1_chorus_pro_factures_valideur_consulter_post import BodyValideurConsulterFactureApiV1ChorusProFacturesValideurConsulterPost
from factpulse.models.body_valideur_rechercher_factures_api_v1_chorus_pro_factures_valideur_rechercher_post import BodyValideurRechercherFacturesApiV1ChorusProFacturesValideurRechercherPost
from factpulse.models.body_valideur_traiter_facture_api_v1_chorus_pro_factures_valideur_traiter_post import BodyValideurTraiterFactureApiV1ChorusProFacturesValideurTraiterPost
from factpulse.models.consulter_facture_request import ConsulterFactureRequest
from factpulse.models.consulter_facture_response import ConsulterFactureResponse
from factpulse.models.consulter_structure_request import ConsulterStructureRequest
from factpulse.models.consulter_structure_response import ConsulterStructureResponse
from factpulse.models.obtenir_id_chorus_pro_request import ObtenirIdChorusProRequest
from factpulse.models.obtenir_id_chorus_pro_response import ObtenirIdChorusProResponse
from factpulse.models.rechercher_services_response import RechercherServicesResponse
from factpulse.models.rechercher_structure_request import RechercherStructureRequest
from factpulse.models.rechercher_structure_response import RechercherStructureResponse
from factpulse.models.soumettre_facture_request import SoumettreFactureRequest
from factpulse.models.soumettre_facture_response import SoumettreFactureResponse

from factpulse.api_client import ApiClient, RequestSerialized
from factpulse.api_response import ApiResponse
from factpulse.rest import RESTResponseType


class ChorusProApi:
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None) -> None:
        if api_client is None:
            api_client = ApiClient.get_default()
        self.api_client = api_client


    @validate_call
    def ajouter_fichier_api_v1_chorus_pro_transverses_ajouter_fichier_post(
        self,
        body_ajouter_fichier_api_v1_chorus_pro_transverses_ajouter_fichier_post: BodyAjouterFichierApiV1ChorusProTransversesAjouterFichierPost,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> object:
        """Ajouter une pièce jointe

        Ajoute une pièce jointe au compte utilisateur courant.      **Taille max** : 10 Mo par fichier      **Payload exemple** :     ```json     {       \"pieceJointeFichier\": \"JVBERi0xLjQKJeLjz9MKNSAwIG9iago8P...\",       \"pieceJointeNom\": \"bon_commande.pdf\",       \"pieceJointeTypeMime\": \"application/pdf\",       \"pieceJointeExtension\": \"PDF\"     }     ```      **Retour** : L'ID de la pièce jointe (`pieceJointeIdFichier`) à utiliser ensuite dans `/factures/completer`.      **Extensions acceptées** : PDF, JPG, PNG, ZIP, XML, etc.

        :param body_ajouter_fichier_api_v1_chorus_pro_transverses_ajouter_fichier_post: (required)
        :type body_ajouter_fichier_api_v1_chorus_pro_transverses_ajouter_fichier_post: BodyAjouterFichierApiV1ChorusProTransversesAjouterFichierPost
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._ajouter_fichier_api_v1_chorus_pro_transverses_ajouter_fichier_post_serialize(
            body_ajouter_fichier_api_v1_chorus_pro_transverses_ajouter_fichier_post=body_ajouter_fichier_api_v1_chorus_pro_transverses_ajouter_fichier_post,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def ajouter_fichier_api_v1_chorus_pro_transverses_ajouter_fichier_post_with_http_info(
        self,
        body_ajouter_fichier_api_v1_chorus_pro_transverses_ajouter_fichier_post: BodyAjouterFichierApiV1ChorusProTransversesAjouterFichierPost,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[object]:
        """Ajouter une pièce jointe

        Ajoute une pièce jointe au compte utilisateur courant.      **Taille max** : 10 Mo par fichier      **Payload exemple** :     ```json     {       \"pieceJointeFichier\": \"JVBERi0xLjQKJeLjz9MKNSAwIG9iago8P...\",       \"pieceJointeNom\": \"bon_commande.pdf\",       \"pieceJointeTypeMime\": \"application/pdf\",       \"pieceJointeExtension\": \"PDF\"     }     ```      **Retour** : L'ID de la pièce jointe (`pieceJointeIdFichier`) à utiliser ensuite dans `/factures/completer`.      **Extensions acceptées** : PDF, JPG, PNG, ZIP, XML, etc.

        :param body_ajouter_fichier_api_v1_chorus_pro_transverses_ajouter_fichier_post: (required)
        :type body_ajouter_fichier_api_v1_chorus_pro_transverses_ajouter_fichier_post: BodyAjouterFichierApiV1ChorusProTransversesAjouterFichierPost
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._ajouter_fichier_api_v1_chorus_pro_transverses_ajouter_fichier_post_serialize(
            body_ajouter_fichier_api_v1_chorus_pro_transverses_ajouter_fichier_post=body_ajouter_fichier_api_v1_chorus_pro_transverses_ajouter_fichier_post,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def ajouter_fichier_api_v1_chorus_pro_transverses_ajouter_fichier_post_without_preload_content(
        self,
        body_ajouter_fichier_api_v1_chorus_pro_transverses_ajouter_fichier_post: BodyAjouterFichierApiV1ChorusProTransversesAjouterFichierPost,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Ajouter une pièce jointe

        Ajoute une pièce jointe au compte utilisateur courant.      **Taille max** : 10 Mo par fichier      **Payload exemple** :     ```json     {       \"pieceJointeFichier\": \"JVBERi0xLjQKJeLjz9MKNSAwIG9iago8P...\",       \"pieceJointeNom\": \"bon_commande.pdf\",       \"pieceJointeTypeMime\": \"application/pdf\",       \"pieceJointeExtension\": \"PDF\"     }     ```      **Retour** : L'ID de la pièce jointe (`pieceJointeIdFichier`) à utiliser ensuite dans `/factures/completer`.      **Extensions acceptées** : PDF, JPG, PNG, ZIP, XML, etc.

        :param body_ajouter_fichier_api_v1_chorus_pro_transverses_ajouter_fichier_post: (required)
        :type body_ajouter_fichier_api_v1_chorus_pro_transverses_ajouter_fichier_post: BodyAjouterFichierApiV1ChorusProTransversesAjouterFichierPost
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._ajouter_fichier_api_v1_chorus_pro_transverses_ajouter_fichier_post_serialize(
            body_ajouter_fichier_api_v1_chorus_pro_transverses_ajouter_fichier_post=body_ajouter_fichier_api_v1_chorus_pro_transverses_ajouter_fichier_post,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _ajouter_fichier_api_v1_chorus_pro_transverses_ajouter_fichier_post_serialize(
        self,
        body_ajouter_fichier_api_v1_chorus_pro_transverses_ajouter_fichier_post,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if body_ajouter_fichier_api_v1_chorus_pro_transverses_ajouter_fichier_post is not None:
            _body_params = body_ajouter_fichier_api_v1_chorus_pro_transverses_ajouter_fichier_post


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'HTTPBearer'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/api/v1/chorus-pro/transverses/ajouter-fichier',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def completer_facture_api_v1_chorus_pro_factures_completer_post(
        self,
        body_completer_facture_api_v1_chorus_pro_factures_completer_post: BodyCompleterFactureApiV1ChorusProFacturesCompleterPost,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> object:
        """Compléter une facture suspendue (Fournisseur)

        Complète une facture au statut SUSPENDUE en ajoutant des pièces jointes ou un commentaire.      **Statut requis** : SUSPENDUE      **Actions possibles** :     - Ajouter des pièces jointes (justificatifs, bons de commande, etc.)     - Modifier le commentaire      **Payload exemple** :     ```json     {       \"identifiantFactureCPP\": 12345,       \"commentaire\": \"Voici les justificatifs demandés\",       \"listePiecesJointes\": [         {           \"pieceJointeIdFichier\": 98765,           \"pieceJointeNom\": \"bon_commande.pdf\"         }       ]     }     ```      **Note** : Les pièces jointes doivent d'abord être uploadées via `/transverses/ajouter-fichier`.      **Après complétion** : La facture repasse au statut MISE_A_DISPOSITION.

        :param body_completer_facture_api_v1_chorus_pro_factures_completer_post: (required)
        :type body_completer_facture_api_v1_chorus_pro_factures_completer_post: BodyCompleterFactureApiV1ChorusProFacturesCompleterPost
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._completer_facture_api_v1_chorus_pro_factures_completer_post_serialize(
            body_completer_facture_api_v1_chorus_pro_factures_completer_post=body_completer_facture_api_v1_chorus_pro_factures_completer_post,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def completer_facture_api_v1_chorus_pro_factures_completer_post_with_http_info(
        self,
        body_completer_facture_api_v1_chorus_pro_factures_completer_post: BodyCompleterFactureApiV1ChorusProFacturesCompleterPost,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[object]:
        """Compléter une facture suspendue (Fournisseur)

        Complète une facture au statut SUSPENDUE en ajoutant des pièces jointes ou un commentaire.      **Statut requis** : SUSPENDUE      **Actions possibles** :     - Ajouter des pièces jointes (justificatifs, bons de commande, etc.)     - Modifier le commentaire      **Payload exemple** :     ```json     {       \"identifiantFactureCPP\": 12345,       \"commentaire\": \"Voici les justificatifs demandés\",       \"listePiecesJointes\": [         {           \"pieceJointeIdFichier\": 98765,           \"pieceJointeNom\": \"bon_commande.pdf\"         }       ]     }     ```      **Note** : Les pièces jointes doivent d'abord être uploadées via `/transverses/ajouter-fichier`.      **Après complétion** : La facture repasse au statut MISE_A_DISPOSITION.

        :param body_completer_facture_api_v1_chorus_pro_factures_completer_post: (required)
        :type body_completer_facture_api_v1_chorus_pro_factures_completer_post: BodyCompleterFactureApiV1ChorusProFacturesCompleterPost
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._completer_facture_api_v1_chorus_pro_factures_completer_post_serialize(
            body_completer_facture_api_v1_chorus_pro_factures_completer_post=body_completer_facture_api_v1_chorus_pro_factures_completer_post,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def completer_facture_api_v1_chorus_pro_factures_completer_post_without_preload_content(
        self,
        body_completer_facture_api_v1_chorus_pro_factures_completer_post: BodyCompleterFactureApiV1ChorusProFacturesCompleterPost,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Compléter une facture suspendue (Fournisseur)

        Complète une facture au statut SUSPENDUE en ajoutant des pièces jointes ou un commentaire.      **Statut requis** : SUSPENDUE      **Actions possibles** :     - Ajouter des pièces jointes (justificatifs, bons de commande, etc.)     - Modifier le commentaire      **Payload exemple** :     ```json     {       \"identifiantFactureCPP\": 12345,       \"commentaire\": \"Voici les justificatifs demandés\",       \"listePiecesJointes\": [         {           \"pieceJointeIdFichier\": 98765,           \"pieceJointeNom\": \"bon_commande.pdf\"         }       ]     }     ```      **Note** : Les pièces jointes doivent d'abord être uploadées via `/transverses/ajouter-fichier`.      **Après complétion** : La facture repasse au statut MISE_A_DISPOSITION.

        :param body_completer_facture_api_v1_chorus_pro_factures_completer_post: (required)
        :type body_completer_facture_api_v1_chorus_pro_factures_completer_post: BodyCompleterFactureApiV1ChorusProFacturesCompleterPost
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._completer_facture_api_v1_chorus_pro_factures_completer_post_serialize(
            body_completer_facture_api_v1_chorus_pro_factures_completer_post=body_completer_facture_api_v1_chorus_pro_factures_completer_post,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _completer_facture_api_v1_chorus_pro_factures_completer_post_serialize(
        self,
        body_completer_facture_api_v1_chorus_pro_factures_completer_post,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if body_completer_facture_api_v1_chorus_pro_factures_completer_post is not None:
            _body_params = body_completer_facture_api_v1_chorus_pro_factures_completer_post


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'HTTPBearer'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/api/v1/chorus-pro/factures/completer',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def consulter_facture_api_v1_chorus_pro_factures_consulter_post(
        self,
        consulter_facture_request: ConsulterFactureRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ConsulterFactureResponse:
        """Consulter le statut d'une facture

        Récupère les informations et le statut actuel d'une facture soumise à Chorus Pro.      **Retour** :     - Numéro et date de facture     - Montant TTC     - **Statut courant** : SOUMISE, VALIDEE, REJETEE, SUSPENDUE, MANDATEE, MISE_EN_PAIEMENT, etc.     - Structure destinataire      **Cas d'usage** :     - Suivre l'évolution du traitement d'une facture     - Vérifier si une facture a été validée ou rejetée     - Obtenir la date de mise en paiement      **Polling** : Appelez cet endpoint régulièrement pour suivre l'évolution du statut.

        :param consulter_facture_request: (required)
        :type consulter_facture_request: ConsulterFactureRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._consulter_facture_api_v1_chorus_pro_factures_consulter_post_serialize(
            consulter_facture_request=consulter_facture_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ConsulterFactureResponse",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def consulter_facture_api_v1_chorus_pro_factures_consulter_post_with_http_info(
        self,
        consulter_facture_request: ConsulterFactureRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[ConsulterFactureResponse]:
        """Consulter le statut d'une facture

        Récupère les informations et le statut actuel d'une facture soumise à Chorus Pro.      **Retour** :     - Numéro et date de facture     - Montant TTC     - **Statut courant** : SOUMISE, VALIDEE, REJETEE, SUSPENDUE, MANDATEE, MISE_EN_PAIEMENT, etc.     - Structure destinataire      **Cas d'usage** :     - Suivre l'évolution du traitement d'une facture     - Vérifier si une facture a été validée ou rejetée     - Obtenir la date de mise en paiement      **Polling** : Appelez cet endpoint régulièrement pour suivre l'évolution du statut.

        :param consulter_facture_request: (required)
        :type consulter_facture_request: ConsulterFactureRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._consulter_facture_api_v1_chorus_pro_factures_consulter_post_serialize(
            consulter_facture_request=consulter_facture_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ConsulterFactureResponse",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def consulter_facture_api_v1_chorus_pro_factures_consulter_post_without_preload_content(
        self,
        consulter_facture_request: ConsulterFactureRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Consulter le statut d'une facture

        Récupère les informations et le statut actuel d'une facture soumise à Chorus Pro.      **Retour** :     - Numéro et date de facture     - Montant TTC     - **Statut courant** : SOUMISE, VALIDEE, REJETEE, SUSPENDUE, MANDATEE, MISE_EN_PAIEMENT, etc.     - Structure destinataire      **Cas d'usage** :     - Suivre l'évolution du traitement d'une facture     - Vérifier si une facture a été validée ou rejetée     - Obtenir la date de mise en paiement      **Polling** : Appelez cet endpoint régulièrement pour suivre l'évolution du statut.

        :param consulter_facture_request: (required)
        :type consulter_facture_request: ConsulterFactureRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._consulter_facture_api_v1_chorus_pro_factures_consulter_post_serialize(
            consulter_facture_request=consulter_facture_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ConsulterFactureResponse",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _consulter_facture_api_v1_chorus_pro_factures_consulter_post_serialize(
        self,
        consulter_facture_request,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if consulter_facture_request is not None:
            _body_params = consulter_facture_request


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'HTTPBearer'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/api/v1/chorus-pro/factures/consulter',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def consulter_structure_api_v1_chorus_pro_structures_consulter_post(
        self,
        consulter_structure_request: ConsulterStructureRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ConsulterStructureResponse:
        """Consulter les détails d'une structure

        Récupère les informations détaillées d'une structure Chorus Pro.       **Retour** :     - Raison sociale     - Numéro de TVA intracommunautaire     - Email de contact     - **Paramètres obligatoires** : Indique si le code service et/ou numéro d'engagement sont requis pour soumettre une facture      **Étape typique** : Appelée après `rechercher-structures` pour savoir quels champs sont obligatoires avant de soumettre une facture.

        :param consulter_structure_request: (required)
        :type consulter_structure_request: ConsulterStructureRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._consulter_structure_api_v1_chorus_pro_structures_consulter_post_serialize(
            consulter_structure_request=consulter_structure_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ConsulterStructureResponse",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def consulter_structure_api_v1_chorus_pro_structures_consulter_post_with_http_info(
        self,
        consulter_structure_request: ConsulterStructureRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[ConsulterStructureResponse]:
        """Consulter les détails d'une structure

        Récupère les informations détaillées d'une structure Chorus Pro.       **Retour** :     - Raison sociale     - Numéro de TVA intracommunautaire     - Email de contact     - **Paramètres obligatoires** : Indique si le code service et/ou numéro d'engagement sont requis pour soumettre une facture      **Étape typique** : Appelée après `rechercher-structures` pour savoir quels champs sont obligatoires avant de soumettre une facture.

        :param consulter_structure_request: (required)
        :type consulter_structure_request: ConsulterStructureRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._consulter_structure_api_v1_chorus_pro_structures_consulter_post_serialize(
            consulter_structure_request=consulter_structure_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ConsulterStructureResponse",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def consulter_structure_api_v1_chorus_pro_structures_consulter_post_without_preload_content(
        self,
        consulter_structure_request: ConsulterStructureRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Consulter les détails d'une structure

        Récupère les informations détaillées d'une structure Chorus Pro.       **Retour** :     - Raison sociale     - Numéro de TVA intracommunautaire     - Email de contact     - **Paramètres obligatoires** : Indique si le code service et/ou numéro d'engagement sont requis pour soumettre une facture      **Étape typique** : Appelée après `rechercher-structures` pour savoir quels champs sont obligatoires avant de soumettre une facture.

        :param consulter_structure_request: (required)
        :type consulter_structure_request: ConsulterStructureRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._consulter_structure_api_v1_chorus_pro_structures_consulter_post_serialize(
            consulter_structure_request=consulter_structure_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ConsulterStructureResponse",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _consulter_structure_api_v1_chorus_pro_structures_consulter_post_serialize(
        self,
        consulter_structure_request,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if consulter_structure_request is not None:
            _body_params = consulter_structure_request


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'HTTPBearer'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/api/v1/chorus-pro/structures/consulter',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def lister_services_structure_api_v1_chorus_pro_structures_id_structure_cpp_services_get(
        self,
        id_structure_cpp: StrictInt,
        body_lister_services_structure_api_v1_chorus_pro_structures_id_structure_cpp_services_get: BodyListerServicesStructureApiV1ChorusProStructuresIdStructureCppServicesGet,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RechercherServicesResponse:
        """Lister les services d'une structure

        Récupère la liste des services actifs d'une structure publique.      **Cas d'usage** :     - Lister les services disponibles pour une administration     - Vérifier qu'un code service existe avant de soumettre une facture      **Retour** :     - Liste des services avec leur code, libellé et statut (actif/inactif)

        :param id_structure_cpp: (required)
        :type id_structure_cpp: int
        :param body_lister_services_structure_api_v1_chorus_pro_structures_id_structure_cpp_services_get: (required)
        :type body_lister_services_structure_api_v1_chorus_pro_structures_id_structure_cpp_services_get: BodyListerServicesStructureApiV1ChorusProStructuresIdStructureCppServicesGet
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._lister_services_structure_api_v1_chorus_pro_structures_id_structure_cpp_services_get_serialize(
            id_structure_cpp=id_structure_cpp,
            body_lister_services_structure_api_v1_chorus_pro_structures_id_structure_cpp_services_get=body_lister_services_structure_api_v1_chorus_pro_structures_id_structure_cpp_services_get,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "RechercherServicesResponse",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def lister_services_structure_api_v1_chorus_pro_structures_id_structure_cpp_services_get_with_http_info(
        self,
        id_structure_cpp: StrictInt,
        body_lister_services_structure_api_v1_chorus_pro_structures_id_structure_cpp_services_get: BodyListerServicesStructureApiV1ChorusProStructuresIdStructureCppServicesGet,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[RechercherServicesResponse]:
        """Lister les services d'une structure

        Récupère la liste des services actifs d'une structure publique.      **Cas d'usage** :     - Lister les services disponibles pour une administration     - Vérifier qu'un code service existe avant de soumettre une facture      **Retour** :     - Liste des services avec leur code, libellé et statut (actif/inactif)

        :param id_structure_cpp: (required)
        :type id_structure_cpp: int
        :param body_lister_services_structure_api_v1_chorus_pro_structures_id_structure_cpp_services_get: (required)
        :type body_lister_services_structure_api_v1_chorus_pro_structures_id_structure_cpp_services_get: BodyListerServicesStructureApiV1ChorusProStructuresIdStructureCppServicesGet
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._lister_services_structure_api_v1_chorus_pro_structures_id_structure_cpp_services_get_serialize(
            id_structure_cpp=id_structure_cpp,
            body_lister_services_structure_api_v1_chorus_pro_structures_id_structure_cpp_services_get=body_lister_services_structure_api_v1_chorus_pro_structures_id_structure_cpp_services_get,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "RechercherServicesResponse",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def lister_services_structure_api_v1_chorus_pro_structures_id_structure_cpp_services_get_without_preload_content(
        self,
        id_structure_cpp: StrictInt,
        body_lister_services_structure_api_v1_chorus_pro_structures_id_structure_cpp_services_get: BodyListerServicesStructureApiV1ChorusProStructuresIdStructureCppServicesGet,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Lister les services d'une structure

        Récupère la liste des services actifs d'une structure publique.      **Cas d'usage** :     - Lister les services disponibles pour une administration     - Vérifier qu'un code service existe avant de soumettre une facture      **Retour** :     - Liste des services avec leur code, libellé et statut (actif/inactif)

        :param id_structure_cpp: (required)
        :type id_structure_cpp: int
        :param body_lister_services_structure_api_v1_chorus_pro_structures_id_structure_cpp_services_get: (required)
        :type body_lister_services_structure_api_v1_chorus_pro_structures_id_structure_cpp_services_get: BodyListerServicesStructureApiV1ChorusProStructuresIdStructureCppServicesGet
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._lister_services_structure_api_v1_chorus_pro_structures_id_structure_cpp_services_get_serialize(
            id_structure_cpp=id_structure_cpp,
            body_lister_services_structure_api_v1_chorus_pro_structures_id_structure_cpp_services_get=body_lister_services_structure_api_v1_chorus_pro_structures_id_structure_cpp_services_get,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "RechercherServicesResponse",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _lister_services_structure_api_v1_chorus_pro_structures_id_structure_cpp_services_get_serialize(
        self,
        id_structure_cpp,
        body_lister_services_structure_api_v1_chorus_pro_structures_id_structure_cpp_services_get,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        if id_structure_cpp is not None:
            _path_params['id_structure_cpp'] = id_structure_cpp
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if body_lister_services_structure_api_v1_chorus_pro_structures_id_structure_cpp_services_get is not None:
            _body_params = body_lister_services_structure_api_v1_chorus_pro_structures_id_structure_cpp_services_get


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'HTTPBearer'
        ]

        return self.api_client.param_serialize(
            method='GET',
            resource_path='/api/v1/chorus-pro/structures/{id_structure_cpp}/services',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def obtenir_id_chorus_pro_depuis_siret_api_v1_chorus_pro_structures_obtenir_id_depuis_siret_post(
        self,
        obtenir_id_chorus_pro_request: ObtenirIdChorusProRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ObtenirIdChorusProResponse:
        """Utilitaire : Obtenir l'ID Chorus Pro depuis un SIRET

        **Utilitaire pratique** pour obtenir l'ID Chorus Pro d'une structure à partir de son SIRET.       Cette fonction wrapper combine :     1. Recherche de la structure par SIRET     2. Extraction de l'`id_structure_cpp` si une seule structure est trouvée      **Retour** :     - `id_structure_cpp` : ID Chorus Pro (0 si non trouvé ou si plusieurs résultats)     - `designation_structure` : Nom de la structure (si trouvée)     - `message` : Message explicatif      **Cas d'usage** :     - Raccourci pour obtenir directement l'ID Chorus Pro avant de soumettre une facture     - Alternative simplifiée à `rechercher-structures` + extraction manuelle de l'ID      **Note** : Si plusieurs structures correspondent au SIRET (rare), retourne 0 et un message d'erreur.

        :param obtenir_id_chorus_pro_request: (required)
        :type obtenir_id_chorus_pro_request: ObtenirIdChorusProRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._obtenir_id_chorus_pro_depuis_siret_api_v1_chorus_pro_structures_obtenir_id_depuis_siret_post_serialize(
            obtenir_id_chorus_pro_request=obtenir_id_chorus_pro_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ObtenirIdChorusProResponse",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def obtenir_id_chorus_pro_depuis_siret_api_v1_chorus_pro_structures_obtenir_id_depuis_siret_post_with_http_info(
        self,
        obtenir_id_chorus_pro_request: ObtenirIdChorusProRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[ObtenirIdChorusProResponse]:
        """Utilitaire : Obtenir l'ID Chorus Pro depuis un SIRET

        **Utilitaire pratique** pour obtenir l'ID Chorus Pro d'une structure à partir de son SIRET.       Cette fonction wrapper combine :     1. Recherche de la structure par SIRET     2. Extraction de l'`id_structure_cpp` si une seule structure est trouvée      **Retour** :     - `id_structure_cpp` : ID Chorus Pro (0 si non trouvé ou si plusieurs résultats)     - `designation_structure` : Nom de la structure (si trouvée)     - `message` : Message explicatif      **Cas d'usage** :     - Raccourci pour obtenir directement l'ID Chorus Pro avant de soumettre une facture     - Alternative simplifiée à `rechercher-structures` + extraction manuelle de l'ID      **Note** : Si plusieurs structures correspondent au SIRET (rare), retourne 0 et un message d'erreur.

        :param obtenir_id_chorus_pro_request: (required)
        :type obtenir_id_chorus_pro_request: ObtenirIdChorusProRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._obtenir_id_chorus_pro_depuis_siret_api_v1_chorus_pro_structures_obtenir_id_depuis_siret_post_serialize(
            obtenir_id_chorus_pro_request=obtenir_id_chorus_pro_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ObtenirIdChorusProResponse",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def obtenir_id_chorus_pro_depuis_siret_api_v1_chorus_pro_structures_obtenir_id_depuis_siret_post_without_preload_content(
        self,
        obtenir_id_chorus_pro_request: ObtenirIdChorusProRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Utilitaire : Obtenir l'ID Chorus Pro depuis un SIRET

        **Utilitaire pratique** pour obtenir l'ID Chorus Pro d'une structure à partir de son SIRET.       Cette fonction wrapper combine :     1. Recherche de la structure par SIRET     2. Extraction de l'`id_structure_cpp` si une seule structure est trouvée      **Retour** :     - `id_structure_cpp` : ID Chorus Pro (0 si non trouvé ou si plusieurs résultats)     - `designation_structure` : Nom de la structure (si trouvée)     - `message` : Message explicatif      **Cas d'usage** :     - Raccourci pour obtenir directement l'ID Chorus Pro avant de soumettre une facture     - Alternative simplifiée à `rechercher-structures` + extraction manuelle de l'ID      **Note** : Si plusieurs structures correspondent au SIRET (rare), retourne 0 et un message d'erreur.

        :param obtenir_id_chorus_pro_request: (required)
        :type obtenir_id_chorus_pro_request: ObtenirIdChorusProRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._obtenir_id_chorus_pro_depuis_siret_api_v1_chorus_pro_structures_obtenir_id_depuis_siret_post_serialize(
            obtenir_id_chorus_pro_request=obtenir_id_chorus_pro_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "ObtenirIdChorusProResponse",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _obtenir_id_chorus_pro_depuis_siret_api_v1_chorus_pro_structures_obtenir_id_depuis_siret_post_serialize(
        self,
        obtenir_id_chorus_pro_request,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if obtenir_id_chorus_pro_request is not None:
            _body_params = obtenir_id_chorus_pro_request


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'HTTPBearer'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/api/v1/chorus-pro/structures/obtenir-id-depuis-siret',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def rechercher_factures_destinataire_api_v1_chorus_pro_factures_rechercher_destinataire_post(
        self,
        body_rechercher_factures_destinataire_api_v1_chorus_pro_factures_rechercher_destinataire_post: BodyRechercherFacturesDestinataireApiV1ChorusProFacturesRechercherDestinatairePost,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> object:
        """Rechercher factures reçues (Destinataire)

        Recherche les factures reçues par le destinataire connecté.      **Filtres** :     - Téléchargée / non téléchargée     - Dates de réception     - Statut (MISE_A_DISPOSITION, SUSPENDUE, etc.)     - Fournisseur      **Indicateur utile** : `factureTelechargeeParDestinataire` permet de savoir si la facture a déjà été téléchargée.

        :param body_rechercher_factures_destinataire_api_v1_chorus_pro_factures_rechercher_destinataire_post: (required)
        :type body_rechercher_factures_destinataire_api_v1_chorus_pro_factures_rechercher_destinataire_post: BodyRechercherFacturesDestinataireApiV1ChorusProFacturesRechercherDestinatairePost
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._rechercher_factures_destinataire_api_v1_chorus_pro_factures_rechercher_destinataire_post_serialize(
            body_rechercher_factures_destinataire_api_v1_chorus_pro_factures_rechercher_destinataire_post=body_rechercher_factures_destinataire_api_v1_chorus_pro_factures_rechercher_destinataire_post,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def rechercher_factures_destinataire_api_v1_chorus_pro_factures_rechercher_destinataire_post_with_http_info(
        self,
        body_rechercher_factures_destinataire_api_v1_chorus_pro_factures_rechercher_destinataire_post: BodyRechercherFacturesDestinataireApiV1ChorusProFacturesRechercherDestinatairePost,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[object]:
        """Rechercher factures reçues (Destinataire)

        Recherche les factures reçues par le destinataire connecté.      **Filtres** :     - Téléchargée / non téléchargée     - Dates de réception     - Statut (MISE_A_DISPOSITION, SUSPENDUE, etc.)     - Fournisseur      **Indicateur utile** : `factureTelechargeeParDestinataire` permet de savoir si la facture a déjà été téléchargée.

        :param body_rechercher_factures_destinataire_api_v1_chorus_pro_factures_rechercher_destinataire_post: (required)
        :type body_rechercher_factures_destinataire_api_v1_chorus_pro_factures_rechercher_destinataire_post: BodyRechercherFacturesDestinataireApiV1ChorusProFacturesRechercherDestinatairePost
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._rechercher_factures_destinataire_api_v1_chorus_pro_factures_rechercher_destinataire_post_serialize(
            body_rechercher_factures_destinataire_api_v1_chorus_pro_factures_rechercher_destinataire_post=body_rechercher_factures_destinataire_api_v1_chorus_pro_factures_rechercher_destinataire_post,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def rechercher_factures_destinataire_api_v1_chorus_pro_factures_rechercher_destinataire_post_without_preload_content(
        self,
        body_rechercher_factures_destinataire_api_v1_chorus_pro_factures_rechercher_destinataire_post: BodyRechercherFacturesDestinataireApiV1ChorusProFacturesRechercherDestinatairePost,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Rechercher factures reçues (Destinataire)

        Recherche les factures reçues par le destinataire connecté.      **Filtres** :     - Téléchargée / non téléchargée     - Dates de réception     - Statut (MISE_A_DISPOSITION, SUSPENDUE, etc.)     - Fournisseur      **Indicateur utile** : `factureTelechargeeParDestinataire` permet de savoir si la facture a déjà été téléchargée.

        :param body_rechercher_factures_destinataire_api_v1_chorus_pro_factures_rechercher_destinataire_post: (required)
        :type body_rechercher_factures_destinataire_api_v1_chorus_pro_factures_rechercher_destinataire_post: BodyRechercherFacturesDestinataireApiV1ChorusProFacturesRechercherDestinatairePost
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._rechercher_factures_destinataire_api_v1_chorus_pro_factures_rechercher_destinataire_post_serialize(
            body_rechercher_factures_destinataire_api_v1_chorus_pro_factures_rechercher_destinataire_post=body_rechercher_factures_destinataire_api_v1_chorus_pro_factures_rechercher_destinataire_post,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _rechercher_factures_destinataire_api_v1_chorus_pro_factures_rechercher_destinataire_post_serialize(
        self,
        body_rechercher_factures_destinataire_api_v1_chorus_pro_factures_rechercher_destinataire_post,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if body_rechercher_factures_destinataire_api_v1_chorus_pro_factures_rechercher_destinataire_post is not None:
            _body_params = body_rechercher_factures_destinataire_api_v1_chorus_pro_factures_rechercher_destinataire_post


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'HTTPBearer'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/api/v1/chorus-pro/factures/rechercher-destinataire',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def rechercher_factures_fournisseur_api_v1_chorus_pro_factures_rechercher_fournisseur_post(
        self,
        body_rechercher_factures_fournisseur_api_v1_chorus_pro_factures_rechercher_fournisseur_post: BodyRechercherFacturesFournisseurApiV1ChorusProFacturesRechercherFournisseurPost,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> object:
        """Rechercher factures émises (Fournisseur)

        Recherche les factures émises par le fournisseur connecté.      **Filtres disponibles** :     - Numéro de facture     - Dates (début/fin)     - Statut     - Structure destinataire     - Montant      **Cas d'usage** :     - Suivi des factures émises     - Vérification des statuts     - Export pour comptabilité

        :param body_rechercher_factures_fournisseur_api_v1_chorus_pro_factures_rechercher_fournisseur_post: (required)
        :type body_rechercher_factures_fournisseur_api_v1_chorus_pro_factures_rechercher_fournisseur_post: BodyRechercherFacturesFournisseurApiV1ChorusProFacturesRechercherFournisseurPost
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._rechercher_factures_fournisseur_api_v1_chorus_pro_factures_rechercher_fournisseur_post_serialize(
            body_rechercher_factures_fournisseur_api_v1_chorus_pro_factures_rechercher_fournisseur_post=body_rechercher_factures_fournisseur_api_v1_chorus_pro_factures_rechercher_fournisseur_post,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def rechercher_factures_fournisseur_api_v1_chorus_pro_factures_rechercher_fournisseur_post_with_http_info(
        self,
        body_rechercher_factures_fournisseur_api_v1_chorus_pro_factures_rechercher_fournisseur_post: BodyRechercherFacturesFournisseurApiV1ChorusProFacturesRechercherFournisseurPost,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[object]:
        """Rechercher factures émises (Fournisseur)

        Recherche les factures émises par le fournisseur connecté.      **Filtres disponibles** :     - Numéro de facture     - Dates (début/fin)     - Statut     - Structure destinataire     - Montant      **Cas d'usage** :     - Suivi des factures émises     - Vérification des statuts     - Export pour comptabilité

        :param body_rechercher_factures_fournisseur_api_v1_chorus_pro_factures_rechercher_fournisseur_post: (required)
        :type body_rechercher_factures_fournisseur_api_v1_chorus_pro_factures_rechercher_fournisseur_post: BodyRechercherFacturesFournisseurApiV1ChorusProFacturesRechercherFournisseurPost
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._rechercher_factures_fournisseur_api_v1_chorus_pro_factures_rechercher_fournisseur_post_serialize(
            body_rechercher_factures_fournisseur_api_v1_chorus_pro_factures_rechercher_fournisseur_post=body_rechercher_factures_fournisseur_api_v1_chorus_pro_factures_rechercher_fournisseur_post,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def rechercher_factures_fournisseur_api_v1_chorus_pro_factures_rechercher_fournisseur_post_without_preload_content(
        self,
        body_rechercher_factures_fournisseur_api_v1_chorus_pro_factures_rechercher_fournisseur_post: BodyRechercherFacturesFournisseurApiV1ChorusProFacturesRechercherFournisseurPost,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Rechercher factures émises (Fournisseur)

        Recherche les factures émises par le fournisseur connecté.      **Filtres disponibles** :     - Numéro de facture     - Dates (début/fin)     - Statut     - Structure destinataire     - Montant      **Cas d'usage** :     - Suivi des factures émises     - Vérification des statuts     - Export pour comptabilité

        :param body_rechercher_factures_fournisseur_api_v1_chorus_pro_factures_rechercher_fournisseur_post: (required)
        :type body_rechercher_factures_fournisseur_api_v1_chorus_pro_factures_rechercher_fournisseur_post: BodyRechercherFacturesFournisseurApiV1ChorusProFacturesRechercherFournisseurPost
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._rechercher_factures_fournisseur_api_v1_chorus_pro_factures_rechercher_fournisseur_post_serialize(
            body_rechercher_factures_fournisseur_api_v1_chorus_pro_factures_rechercher_fournisseur_post=body_rechercher_factures_fournisseur_api_v1_chorus_pro_factures_rechercher_fournisseur_post,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _rechercher_factures_fournisseur_api_v1_chorus_pro_factures_rechercher_fournisseur_post_serialize(
        self,
        body_rechercher_factures_fournisseur_api_v1_chorus_pro_factures_rechercher_fournisseur_post,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if body_rechercher_factures_fournisseur_api_v1_chorus_pro_factures_rechercher_fournisseur_post is not None:
            _body_params = body_rechercher_factures_fournisseur_api_v1_chorus_pro_factures_rechercher_fournisseur_post


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'HTTPBearer'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/api/v1/chorus-pro/factures/rechercher-fournisseur',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def rechercher_structures_api_v1_chorus_pro_structures_rechercher_post(
        self,
        rechercher_structure_request: RechercherStructureRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RechercherStructureResponse:
        """Rechercher des structures Chorus Pro

        Recherche des structures (entreprises, administrations) enregistrées sur Chorus Pro.      **Cas d'usage** :     - Trouver l'ID Chorus Pro d'une structure à partir de son SIRET     - Vérifier si une structure est enregistrée sur Chorus Pro     - Lister les structures correspondant à des critères      **Filtres disponibles** :     - Identifiant (SIRET, SIREN, etc.)     - Raison sociale     - Type d'identifiant     - Structures privées uniquement      **Étape typique** : Appelée avant `soumettre-facture` pour obtenir l'`id_structure_cpp` du destinataire.

        :param rechercher_structure_request: (required)
        :type rechercher_structure_request: RechercherStructureRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._rechercher_structures_api_v1_chorus_pro_structures_rechercher_post_serialize(
            rechercher_structure_request=rechercher_structure_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "RechercherStructureResponse",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def rechercher_structures_api_v1_chorus_pro_structures_rechercher_post_with_http_info(
        self,
        rechercher_structure_request: RechercherStructureRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[RechercherStructureResponse]:
        """Rechercher des structures Chorus Pro

        Recherche des structures (entreprises, administrations) enregistrées sur Chorus Pro.      **Cas d'usage** :     - Trouver l'ID Chorus Pro d'une structure à partir de son SIRET     - Vérifier si une structure est enregistrée sur Chorus Pro     - Lister les structures correspondant à des critères      **Filtres disponibles** :     - Identifiant (SIRET, SIREN, etc.)     - Raison sociale     - Type d'identifiant     - Structures privées uniquement      **Étape typique** : Appelée avant `soumettre-facture` pour obtenir l'`id_structure_cpp` du destinataire.

        :param rechercher_structure_request: (required)
        :type rechercher_structure_request: RechercherStructureRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._rechercher_structures_api_v1_chorus_pro_structures_rechercher_post_serialize(
            rechercher_structure_request=rechercher_structure_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "RechercherStructureResponse",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def rechercher_structures_api_v1_chorus_pro_structures_rechercher_post_without_preload_content(
        self,
        rechercher_structure_request: RechercherStructureRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Rechercher des structures Chorus Pro

        Recherche des structures (entreprises, administrations) enregistrées sur Chorus Pro.      **Cas d'usage** :     - Trouver l'ID Chorus Pro d'une structure à partir de son SIRET     - Vérifier si une structure est enregistrée sur Chorus Pro     - Lister les structures correspondant à des critères      **Filtres disponibles** :     - Identifiant (SIRET, SIREN, etc.)     - Raison sociale     - Type d'identifiant     - Structures privées uniquement      **Étape typique** : Appelée avant `soumettre-facture` pour obtenir l'`id_structure_cpp` du destinataire.

        :param rechercher_structure_request: (required)
        :type rechercher_structure_request: RechercherStructureRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._rechercher_structures_api_v1_chorus_pro_structures_rechercher_post_serialize(
            rechercher_structure_request=rechercher_structure_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "RechercherStructureResponse",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _rechercher_structures_api_v1_chorus_pro_structures_rechercher_post_serialize(
        self,
        rechercher_structure_request,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if rechercher_structure_request is not None:
            _body_params = rechercher_structure_request


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'HTTPBearer'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/api/v1/chorus-pro/structures/rechercher',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def recycler_facture_api_v1_chorus_pro_factures_recycler_post(
        self,
        body_recycler_facture_api_v1_chorus_pro_factures_recycler_post: BodyRecyclerFactureApiV1ChorusProFacturesRecyclerPost,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> object:
        """Recycler une facture (Fournisseur)

        Recycle une facture au statut A_RECYCLER en modifiant les données d'acheminement.      **Statut requis** : A_RECYCLER      **Champs modifiables** :     - Destinataire (`idStructureCPP`)     - Code service     - Numéro d'engagement      **Cas d'usage** :     - Erreur de destinataire     - Changement de service facturation     - Mise à jour du numéro d'engagement      **Payload exemple** :     ```json     {       \"identifiantFactureCPP\": 12345,       \"idStructureCPP\": 67890,       \"codeService\": \"SERVICE_01\",       \"numeroEngagement\": \"ENG2024001\"     }     ```      **Note** : La facture conserve son numéro et ses montants, seuls les champs d'acheminement changent.

        :param body_recycler_facture_api_v1_chorus_pro_factures_recycler_post: (required)
        :type body_recycler_facture_api_v1_chorus_pro_factures_recycler_post: BodyRecyclerFactureApiV1ChorusProFacturesRecyclerPost
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._recycler_facture_api_v1_chorus_pro_factures_recycler_post_serialize(
            body_recycler_facture_api_v1_chorus_pro_factures_recycler_post=body_recycler_facture_api_v1_chorus_pro_factures_recycler_post,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def recycler_facture_api_v1_chorus_pro_factures_recycler_post_with_http_info(
        self,
        body_recycler_facture_api_v1_chorus_pro_factures_recycler_post: BodyRecyclerFactureApiV1ChorusProFacturesRecyclerPost,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[object]:
        """Recycler une facture (Fournisseur)

        Recycle une facture au statut A_RECYCLER en modifiant les données d'acheminement.      **Statut requis** : A_RECYCLER      **Champs modifiables** :     - Destinataire (`idStructureCPP`)     - Code service     - Numéro d'engagement      **Cas d'usage** :     - Erreur de destinataire     - Changement de service facturation     - Mise à jour du numéro d'engagement      **Payload exemple** :     ```json     {       \"identifiantFactureCPP\": 12345,       \"idStructureCPP\": 67890,       \"codeService\": \"SERVICE_01\",       \"numeroEngagement\": \"ENG2024001\"     }     ```      **Note** : La facture conserve son numéro et ses montants, seuls les champs d'acheminement changent.

        :param body_recycler_facture_api_v1_chorus_pro_factures_recycler_post: (required)
        :type body_recycler_facture_api_v1_chorus_pro_factures_recycler_post: BodyRecyclerFactureApiV1ChorusProFacturesRecyclerPost
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._recycler_facture_api_v1_chorus_pro_factures_recycler_post_serialize(
            body_recycler_facture_api_v1_chorus_pro_factures_recycler_post=body_recycler_facture_api_v1_chorus_pro_factures_recycler_post,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def recycler_facture_api_v1_chorus_pro_factures_recycler_post_without_preload_content(
        self,
        body_recycler_facture_api_v1_chorus_pro_factures_recycler_post: BodyRecyclerFactureApiV1ChorusProFacturesRecyclerPost,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Recycler une facture (Fournisseur)

        Recycle une facture au statut A_RECYCLER en modifiant les données d'acheminement.      **Statut requis** : A_RECYCLER      **Champs modifiables** :     - Destinataire (`idStructureCPP`)     - Code service     - Numéro d'engagement      **Cas d'usage** :     - Erreur de destinataire     - Changement de service facturation     - Mise à jour du numéro d'engagement      **Payload exemple** :     ```json     {       \"identifiantFactureCPP\": 12345,       \"idStructureCPP\": 67890,       \"codeService\": \"SERVICE_01\",       \"numeroEngagement\": \"ENG2024001\"     }     ```      **Note** : La facture conserve son numéro et ses montants, seuls les champs d'acheminement changent.

        :param body_recycler_facture_api_v1_chorus_pro_factures_recycler_post: (required)
        :type body_recycler_facture_api_v1_chorus_pro_factures_recycler_post: BodyRecyclerFactureApiV1ChorusProFacturesRecyclerPost
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._recycler_facture_api_v1_chorus_pro_factures_recycler_post_serialize(
            body_recycler_facture_api_v1_chorus_pro_factures_recycler_post=body_recycler_facture_api_v1_chorus_pro_factures_recycler_post,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _recycler_facture_api_v1_chorus_pro_factures_recycler_post_serialize(
        self,
        body_recycler_facture_api_v1_chorus_pro_factures_recycler_post,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if body_recycler_facture_api_v1_chorus_pro_factures_recycler_post is not None:
            _body_params = body_recycler_facture_api_v1_chorus_pro_factures_recycler_post


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'HTTPBearer'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/api/v1/chorus-pro/factures/recycler',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def soumettre_facture_api_v1_chorus_pro_factures_soumettre_post(
        self,
        soumettre_facture_request: SoumettreFactureRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> SoumettreFactureResponse:
        """Soumettre une facture à Chorus Pro

        Soumet une facture électronique à une structure publique via Chorus Pro.       **📋 Workflow complet** :     1. **Uploader le PDF Factur-X** via `/transverses/ajouter-fichier` → récupérer `pieceJointeId`     2. **Obtenir l'ID structure** via `/structures/rechercher` ou `/structures/obtenir-id-depuis-siret`     3. **Vérifier les paramètres obligatoires** via `/structures/consulter`     4. **Soumettre la facture** avec le `piece_jointe_principale_id` obtenu à l'étape 1      **Pré-requis** :     1. Avoir l'`id_structure_cpp` du destinataire (via `/structures/rechercher`)     2. Connaître les paramètres obligatoires (via `/structures/consulter`) :        - Code service si `code_service_doit_etre_renseigne=true`        - Numéro d'engagement si `numero_ej_doit_etre_renseigne=true`     3. Avoir uploadé le PDF Factur-X (via `/transverses/ajouter-fichier`)      **Format attendu** :     - `piece_jointe_principale_id` : ID retourné par `/transverses/ajouter-fichier`     - Montants : Chaînes de caractères avec 2 décimales (ex: \"1250.50\")     - Dates : Format ISO 8601 (YYYY-MM-DD)      **Retour** :     - `identifiant_facture_cpp` : ID Chorus Pro de la facture créée     - `numero_flux_depot` : Numéro de suivi du dépôt      **Statuts possibles après soumission** :     - SOUMISE : En attente de validation     - VALIDEE : Validée par le destinataire     - REJETEE : Rejetée (erreur de données ou refus métier)     - SUSPENDUE : En attente d'informations complémentaires      **Note** : Utilisez `/factures/consulter` pour suivre l'évolution du statut.

        :param soumettre_facture_request: (required)
        :type soumettre_facture_request: SoumettreFactureRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._soumettre_facture_api_v1_chorus_pro_factures_soumettre_post_serialize(
            soumettre_facture_request=soumettre_facture_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "SoumettreFactureResponse",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def soumettre_facture_api_v1_chorus_pro_factures_soumettre_post_with_http_info(
        self,
        soumettre_facture_request: SoumettreFactureRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[SoumettreFactureResponse]:
        """Soumettre une facture à Chorus Pro

        Soumet une facture électronique à une structure publique via Chorus Pro.       **📋 Workflow complet** :     1. **Uploader le PDF Factur-X** via `/transverses/ajouter-fichier` → récupérer `pieceJointeId`     2. **Obtenir l'ID structure** via `/structures/rechercher` ou `/structures/obtenir-id-depuis-siret`     3. **Vérifier les paramètres obligatoires** via `/structures/consulter`     4. **Soumettre la facture** avec le `piece_jointe_principale_id` obtenu à l'étape 1      **Pré-requis** :     1. Avoir l'`id_structure_cpp` du destinataire (via `/structures/rechercher`)     2. Connaître les paramètres obligatoires (via `/structures/consulter`) :        - Code service si `code_service_doit_etre_renseigne=true`        - Numéro d'engagement si `numero_ej_doit_etre_renseigne=true`     3. Avoir uploadé le PDF Factur-X (via `/transverses/ajouter-fichier`)      **Format attendu** :     - `piece_jointe_principale_id` : ID retourné par `/transverses/ajouter-fichier`     - Montants : Chaînes de caractères avec 2 décimales (ex: \"1250.50\")     - Dates : Format ISO 8601 (YYYY-MM-DD)      **Retour** :     - `identifiant_facture_cpp` : ID Chorus Pro de la facture créée     - `numero_flux_depot` : Numéro de suivi du dépôt      **Statuts possibles après soumission** :     - SOUMISE : En attente de validation     - VALIDEE : Validée par le destinataire     - REJETEE : Rejetée (erreur de données ou refus métier)     - SUSPENDUE : En attente d'informations complémentaires      **Note** : Utilisez `/factures/consulter` pour suivre l'évolution du statut.

        :param soumettre_facture_request: (required)
        :type soumettre_facture_request: SoumettreFactureRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._soumettre_facture_api_v1_chorus_pro_factures_soumettre_post_serialize(
            soumettre_facture_request=soumettre_facture_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "SoumettreFactureResponse",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def soumettre_facture_api_v1_chorus_pro_factures_soumettre_post_without_preload_content(
        self,
        soumettre_facture_request: SoumettreFactureRequest,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Soumettre une facture à Chorus Pro

        Soumet une facture électronique à une structure publique via Chorus Pro.       **📋 Workflow complet** :     1. **Uploader le PDF Factur-X** via `/transverses/ajouter-fichier` → récupérer `pieceJointeId`     2. **Obtenir l'ID structure** via `/structures/rechercher` ou `/structures/obtenir-id-depuis-siret`     3. **Vérifier les paramètres obligatoires** via `/structures/consulter`     4. **Soumettre la facture** avec le `piece_jointe_principale_id` obtenu à l'étape 1      **Pré-requis** :     1. Avoir l'`id_structure_cpp` du destinataire (via `/structures/rechercher`)     2. Connaître les paramètres obligatoires (via `/structures/consulter`) :        - Code service si `code_service_doit_etre_renseigne=true`        - Numéro d'engagement si `numero_ej_doit_etre_renseigne=true`     3. Avoir uploadé le PDF Factur-X (via `/transverses/ajouter-fichier`)      **Format attendu** :     - `piece_jointe_principale_id` : ID retourné par `/transverses/ajouter-fichier`     - Montants : Chaînes de caractères avec 2 décimales (ex: \"1250.50\")     - Dates : Format ISO 8601 (YYYY-MM-DD)      **Retour** :     - `identifiant_facture_cpp` : ID Chorus Pro de la facture créée     - `numero_flux_depot` : Numéro de suivi du dépôt      **Statuts possibles après soumission** :     - SOUMISE : En attente de validation     - VALIDEE : Validée par le destinataire     - REJETEE : Rejetée (erreur de données ou refus métier)     - SUSPENDUE : En attente d'informations complémentaires      **Note** : Utilisez `/factures/consulter` pour suivre l'évolution du statut.

        :param soumettre_facture_request: (required)
        :type soumettre_facture_request: SoumettreFactureRequest
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._soumettre_facture_api_v1_chorus_pro_factures_soumettre_post_serialize(
            soumettre_facture_request=soumettre_facture_request,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "SoumettreFactureResponse",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _soumettre_facture_api_v1_chorus_pro_factures_soumettre_post_serialize(
        self,
        soumettre_facture_request,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if soumettre_facture_request is not None:
            _body_params = soumettre_facture_request


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'HTTPBearer'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/api/v1/chorus-pro/factures/soumettre',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def telecharger_groupe_factures_api_v1_chorus_pro_factures_telecharger_groupe_post(
        self,
        body_telecharger_groupe_factures_api_v1_chorus_pro_factures_telecharger_groupe_post: BodyTelechargerGroupeFacturesApiV1ChorusProFacturesTelechargerGroupePost,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> object:
        """Télécharger un groupe de factures

        Télécharge une ou plusieurs factures (max 10 recommandé) avec leurs pièces jointes.      **Formats disponibles** :     - PDF : Fichier PDF uniquement     - XML : Fichier XML uniquement     - ZIP : Archive contenant PDF + XML + pièces jointes      **Taille maximale** : 120 Mo par téléchargement      **Payload exemple** :     ```json     {       \"listeIdentifiantsFactureCPP\": [12345, 12346],       \"inclurePiecesJointes\": true,       \"formatFichier\": \"ZIP\"     }     ```      **Retour** : Le fichier est encodé en base64 dans le champ `fichierBase64`.      **Note** : Le flag `factureTelechargeeParDestinataire` est mis à jour automatiquement.

        :param body_telecharger_groupe_factures_api_v1_chorus_pro_factures_telecharger_groupe_post: (required)
        :type body_telecharger_groupe_factures_api_v1_chorus_pro_factures_telecharger_groupe_post: BodyTelechargerGroupeFacturesApiV1ChorusProFacturesTelechargerGroupePost
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._telecharger_groupe_factures_api_v1_chorus_pro_factures_telecharger_groupe_post_serialize(
            body_telecharger_groupe_factures_api_v1_chorus_pro_factures_telecharger_groupe_post=body_telecharger_groupe_factures_api_v1_chorus_pro_factures_telecharger_groupe_post,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def telecharger_groupe_factures_api_v1_chorus_pro_factures_telecharger_groupe_post_with_http_info(
        self,
        body_telecharger_groupe_factures_api_v1_chorus_pro_factures_telecharger_groupe_post: BodyTelechargerGroupeFacturesApiV1ChorusProFacturesTelechargerGroupePost,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[object]:
        """Télécharger un groupe de factures

        Télécharge une ou plusieurs factures (max 10 recommandé) avec leurs pièces jointes.      **Formats disponibles** :     - PDF : Fichier PDF uniquement     - XML : Fichier XML uniquement     - ZIP : Archive contenant PDF + XML + pièces jointes      **Taille maximale** : 120 Mo par téléchargement      **Payload exemple** :     ```json     {       \"listeIdentifiantsFactureCPP\": [12345, 12346],       \"inclurePiecesJointes\": true,       \"formatFichier\": \"ZIP\"     }     ```      **Retour** : Le fichier est encodé en base64 dans le champ `fichierBase64`.      **Note** : Le flag `factureTelechargeeParDestinataire` est mis à jour automatiquement.

        :param body_telecharger_groupe_factures_api_v1_chorus_pro_factures_telecharger_groupe_post: (required)
        :type body_telecharger_groupe_factures_api_v1_chorus_pro_factures_telecharger_groupe_post: BodyTelechargerGroupeFacturesApiV1ChorusProFacturesTelechargerGroupePost
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._telecharger_groupe_factures_api_v1_chorus_pro_factures_telecharger_groupe_post_serialize(
            body_telecharger_groupe_factures_api_v1_chorus_pro_factures_telecharger_groupe_post=body_telecharger_groupe_factures_api_v1_chorus_pro_factures_telecharger_groupe_post,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def telecharger_groupe_factures_api_v1_chorus_pro_factures_telecharger_groupe_post_without_preload_content(
        self,
        body_telecharger_groupe_factures_api_v1_chorus_pro_factures_telecharger_groupe_post: BodyTelechargerGroupeFacturesApiV1ChorusProFacturesTelechargerGroupePost,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Télécharger un groupe de factures

        Télécharge une ou plusieurs factures (max 10 recommandé) avec leurs pièces jointes.      **Formats disponibles** :     - PDF : Fichier PDF uniquement     - XML : Fichier XML uniquement     - ZIP : Archive contenant PDF + XML + pièces jointes      **Taille maximale** : 120 Mo par téléchargement      **Payload exemple** :     ```json     {       \"listeIdentifiantsFactureCPP\": [12345, 12346],       \"inclurePiecesJointes\": true,       \"formatFichier\": \"ZIP\"     }     ```      **Retour** : Le fichier est encodé en base64 dans le champ `fichierBase64`.      **Note** : Le flag `factureTelechargeeParDestinataire` est mis à jour automatiquement.

        :param body_telecharger_groupe_factures_api_v1_chorus_pro_factures_telecharger_groupe_post: (required)
        :type body_telecharger_groupe_factures_api_v1_chorus_pro_factures_telecharger_groupe_post: BodyTelechargerGroupeFacturesApiV1ChorusProFacturesTelechargerGroupePost
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._telecharger_groupe_factures_api_v1_chorus_pro_factures_telecharger_groupe_post_serialize(
            body_telecharger_groupe_factures_api_v1_chorus_pro_factures_telecharger_groupe_post=body_telecharger_groupe_factures_api_v1_chorus_pro_factures_telecharger_groupe_post,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _telecharger_groupe_factures_api_v1_chorus_pro_factures_telecharger_groupe_post_serialize(
        self,
        body_telecharger_groupe_factures_api_v1_chorus_pro_factures_telecharger_groupe_post,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if body_telecharger_groupe_factures_api_v1_chorus_pro_factures_telecharger_groupe_post is not None:
            _body_params = body_telecharger_groupe_factures_api_v1_chorus_pro_factures_telecharger_groupe_post


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'HTTPBearer'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/api/v1/chorus-pro/factures/telecharger-groupe',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def traiter_facture_recue_api_v1_chorus_pro_factures_traiter_facture_recue_post(
        self,
        body_traiter_facture_recue_api_v1_chorus_pro_factures_traiter_facture_recue_post: BodyTraiterFactureRecueApiV1ChorusProFacturesTraiterFactureRecuePost,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> object:
        """Traiter une facture reçue (Destinataire)

        Change le statut d'une facture reçue.      **Statuts possibles** :     - MISE_A_DISPOSITION : Facture acceptée     - SUSPENDUE : En attente d'informations complémentaires (motif obligatoire)     - REJETEE : Facture refusée (motif obligatoire)     - MANDATEE : Facture mandatée     - MISE_EN_PAIEMENT : Facture en cours de paiement     - COMPTABILISEE : Facture comptabilisée     - MISE_A_DISPOSITION_COMPTABLE : Mise à disposition comptable     - A_RECYCLER : À recycler     - COMPLETEE : Complétée     - SERVICE-FAIT : Service fait     - PRISE_EN_COMPTE_DESTINATAIRE : Prise en compte     - TRANSMISE_MOA : Transmise à la MOA      **Payload exemple** :     ```json     {       \"identifiantFactureCPP\": 12345,       \"nouveauStatut\": \"REJETEE\",       \"motifRejet\": \"Facture en double\",       \"commentaire\": \"Facture déjà reçue sous la référence ABC123\"     }     ```      **Règles** :     - Un motif est **obligatoire** pour SUSPENDUE et REJETEE     - Seuls certains statuts sont autorisés selon le statut actuel de la facture

        :param body_traiter_facture_recue_api_v1_chorus_pro_factures_traiter_facture_recue_post: (required)
        :type body_traiter_facture_recue_api_v1_chorus_pro_factures_traiter_facture_recue_post: BodyTraiterFactureRecueApiV1ChorusProFacturesTraiterFactureRecuePost
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._traiter_facture_recue_api_v1_chorus_pro_factures_traiter_facture_recue_post_serialize(
            body_traiter_facture_recue_api_v1_chorus_pro_factures_traiter_facture_recue_post=body_traiter_facture_recue_api_v1_chorus_pro_factures_traiter_facture_recue_post,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def traiter_facture_recue_api_v1_chorus_pro_factures_traiter_facture_recue_post_with_http_info(
        self,
        body_traiter_facture_recue_api_v1_chorus_pro_factures_traiter_facture_recue_post: BodyTraiterFactureRecueApiV1ChorusProFacturesTraiterFactureRecuePost,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[object]:
        """Traiter une facture reçue (Destinataire)

        Change le statut d'une facture reçue.      **Statuts possibles** :     - MISE_A_DISPOSITION : Facture acceptée     - SUSPENDUE : En attente d'informations complémentaires (motif obligatoire)     - REJETEE : Facture refusée (motif obligatoire)     - MANDATEE : Facture mandatée     - MISE_EN_PAIEMENT : Facture en cours de paiement     - COMPTABILISEE : Facture comptabilisée     - MISE_A_DISPOSITION_COMPTABLE : Mise à disposition comptable     - A_RECYCLER : À recycler     - COMPLETEE : Complétée     - SERVICE-FAIT : Service fait     - PRISE_EN_COMPTE_DESTINATAIRE : Prise en compte     - TRANSMISE_MOA : Transmise à la MOA      **Payload exemple** :     ```json     {       \"identifiantFactureCPP\": 12345,       \"nouveauStatut\": \"REJETEE\",       \"motifRejet\": \"Facture en double\",       \"commentaire\": \"Facture déjà reçue sous la référence ABC123\"     }     ```      **Règles** :     - Un motif est **obligatoire** pour SUSPENDUE et REJETEE     - Seuls certains statuts sont autorisés selon le statut actuel de la facture

        :param body_traiter_facture_recue_api_v1_chorus_pro_factures_traiter_facture_recue_post: (required)
        :type body_traiter_facture_recue_api_v1_chorus_pro_factures_traiter_facture_recue_post: BodyTraiterFactureRecueApiV1ChorusProFacturesTraiterFactureRecuePost
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._traiter_facture_recue_api_v1_chorus_pro_factures_traiter_facture_recue_post_serialize(
            body_traiter_facture_recue_api_v1_chorus_pro_factures_traiter_facture_recue_post=body_traiter_facture_recue_api_v1_chorus_pro_factures_traiter_facture_recue_post,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def traiter_facture_recue_api_v1_chorus_pro_factures_traiter_facture_recue_post_without_preload_content(
        self,
        body_traiter_facture_recue_api_v1_chorus_pro_factures_traiter_facture_recue_post: BodyTraiterFactureRecueApiV1ChorusProFacturesTraiterFactureRecuePost,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Traiter une facture reçue (Destinataire)

        Change le statut d'une facture reçue.      **Statuts possibles** :     - MISE_A_DISPOSITION : Facture acceptée     - SUSPENDUE : En attente d'informations complémentaires (motif obligatoire)     - REJETEE : Facture refusée (motif obligatoire)     - MANDATEE : Facture mandatée     - MISE_EN_PAIEMENT : Facture en cours de paiement     - COMPTABILISEE : Facture comptabilisée     - MISE_A_DISPOSITION_COMPTABLE : Mise à disposition comptable     - A_RECYCLER : À recycler     - COMPLETEE : Complétée     - SERVICE-FAIT : Service fait     - PRISE_EN_COMPTE_DESTINATAIRE : Prise en compte     - TRANSMISE_MOA : Transmise à la MOA      **Payload exemple** :     ```json     {       \"identifiantFactureCPP\": 12345,       \"nouveauStatut\": \"REJETEE\",       \"motifRejet\": \"Facture en double\",       \"commentaire\": \"Facture déjà reçue sous la référence ABC123\"     }     ```      **Règles** :     - Un motif est **obligatoire** pour SUSPENDUE et REJETEE     - Seuls certains statuts sont autorisés selon le statut actuel de la facture

        :param body_traiter_facture_recue_api_v1_chorus_pro_factures_traiter_facture_recue_post: (required)
        :type body_traiter_facture_recue_api_v1_chorus_pro_factures_traiter_facture_recue_post: BodyTraiterFactureRecueApiV1ChorusProFacturesTraiterFactureRecuePost
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._traiter_facture_recue_api_v1_chorus_pro_factures_traiter_facture_recue_post_serialize(
            body_traiter_facture_recue_api_v1_chorus_pro_factures_traiter_facture_recue_post=body_traiter_facture_recue_api_v1_chorus_pro_factures_traiter_facture_recue_post,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _traiter_facture_recue_api_v1_chorus_pro_factures_traiter_facture_recue_post_serialize(
        self,
        body_traiter_facture_recue_api_v1_chorus_pro_factures_traiter_facture_recue_post,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if body_traiter_facture_recue_api_v1_chorus_pro_factures_traiter_facture_recue_post is not None:
            _body_params = body_traiter_facture_recue_api_v1_chorus_pro_factures_traiter_facture_recue_post


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'HTTPBearer'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/api/v1/chorus-pro/factures/traiter-facture-recue',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def valideur_consulter_facture_api_v1_chorus_pro_factures_valideur_consulter_post(
        self,
        body_valideur_consulter_facture_api_v1_chorus_pro_factures_valideur_consulter_post: BodyValideurConsulterFactureApiV1ChorusProFacturesValideurConsulterPost,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> object:
        """Consulter une facture (Valideur)

        Consulte facture (valideur).

        :param body_valideur_consulter_facture_api_v1_chorus_pro_factures_valideur_consulter_post: (required)
        :type body_valideur_consulter_facture_api_v1_chorus_pro_factures_valideur_consulter_post: BodyValideurConsulterFactureApiV1ChorusProFacturesValideurConsulterPost
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._valideur_consulter_facture_api_v1_chorus_pro_factures_valideur_consulter_post_serialize(
            body_valideur_consulter_facture_api_v1_chorus_pro_factures_valideur_consulter_post=body_valideur_consulter_facture_api_v1_chorus_pro_factures_valideur_consulter_post,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def valideur_consulter_facture_api_v1_chorus_pro_factures_valideur_consulter_post_with_http_info(
        self,
        body_valideur_consulter_facture_api_v1_chorus_pro_factures_valideur_consulter_post: BodyValideurConsulterFactureApiV1ChorusProFacturesValideurConsulterPost,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[object]:
        """Consulter une facture (Valideur)

        Consulte facture (valideur).

        :param body_valideur_consulter_facture_api_v1_chorus_pro_factures_valideur_consulter_post: (required)
        :type body_valideur_consulter_facture_api_v1_chorus_pro_factures_valideur_consulter_post: BodyValideurConsulterFactureApiV1ChorusProFacturesValideurConsulterPost
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._valideur_consulter_facture_api_v1_chorus_pro_factures_valideur_consulter_post_serialize(
            body_valideur_consulter_facture_api_v1_chorus_pro_factures_valideur_consulter_post=body_valideur_consulter_facture_api_v1_chorus_pro_factures_valideur_consulter_post,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def valideur_consulter_facture_api_v1_chorus_pro_factures_valideur_consulter_post_without_preload_content(
        self,
        body_valideur_consulter_facture_api_v1_chorus_pro_factures_valideur_consulter_post: BodyValideurConsulterFactureApiV1ChorusProFacturesValideurConsulterPost,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Consulter une facture (Valideur)

        Consulte facture (valideur).

        :param body_valideur_consulter_facture_api_v1_chorus_pro_factures_valideur_consulter_post: (required)
        :type body_valideur_consulter_facture_api_v1_chorus_pro_factures_valideur_consulter_post: BodyValideurConsulterFactureApiV1ChorusProFacturesValideurConsulterPost
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._valideur_consulter_facture_api_v1_chorus_pro_factures_valideur_consulter_post_serialize(
            body_valideur_consulter_facture_api_v1_chorus_pro_factures_valideur_consulter_post=body_valideur_consulter_facture_api_v1_chorus_pro_factures_valideur_consulter_post,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _valideur_consulter_facture_api_v1_chorus_pro_factures_valideur_consulter_post_serialize(
        self,
        body_valideur_consulter_facture_api_v1_chorus_pro_factures_valideur_consulter_post,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if body_valideur_consulter_facture_api_v1_chorus_pro_factures_valideur_consulter_post is not None:
            _body_params = body_valideur_consulter_facture_api_v1_chorus_pro_factures_valideur_consulter_post


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'HTTPBearer'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/api/v1/chorus-pro/factures/valideur/consulter',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def valideur_rechercher_factures_api_v1_chorus_pro_factures_valideur_rechercher_post(
        self,
        body_valideur_rechercher_factures_api_v1_chorus_pro_factures_valideur_rechercher_post: BodyValideurRechercherFacturesApiV1ChorusProFacturesValideurRechercherPost,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> object:
        """Rechercher factures à valider (Valideur)

        Recherche les factures en attente de validation par le valideur connecté.      **Rôle** : Valideur dans le circuit de validation interne.      **Filtres** : Dates, structure, service, etc.

        :param body_valideur_rechercher_factures_api_v1_chorus_pro_factures_valideur_rechercher_post: (required)
        :type body_valideur_rechercher_factures_api_v1_chorus_pro_factures_valideur_rechercher_post: BodyValideurRechercherFacturesApiV1ChorusProFacturesValideurRechercherPost
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._valideur_rechercher_factures_api_v1_chorus_pro_factures_valideur_rechercher_post_serialize(
            body_valideur_rechercher_factures_api_v1_chorus_pro_factures_valideur_rechercher_post=body_valideur_rechercher_factures_api_v1_chorus_pro_factures_valideur_rechercher_post,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def valideur_rechercher_factures_api_v1_chorus_pro_factures_valideur_rechercher_post_with_http_info(
        self,
        body_valideur_rechercher_factures_api_v1_chorus_pro_factures_valideur_rechercher_post: BodyValideurRechercherFacturesApiV1ChorusProFacturesValideurRechercherPost,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[object]:
        """Rechercher factures à valider (Valideur)

        Recherche les factures en attente de validation par le valideur connecté.      **Rôle** : Valideur dans le circuit de validation interne.      **Filtres** : Dates, structure, service, etc.

        :param body_valideur_rechercher_factures_api_v1_chorus_pro_factures_valideur_rechercher_post: (required)
        :type body_valideur_rechercher_factures_api_v1_chorus_pro_factures_valideur_rechercher_post: BodyValideurRechercherFacturesApiV1ChorusProFacturesValideurRechercherPost
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._valideur_rechercher_factures_api_v1_chorus_pro_factures_valideur_rechercher_post_serialize(
            body_valideur_rechercher_factures_api_v1_chorus_pro_factures_valideur_rechercher_post=body_valideur_rechercher_factures_api_v1_chorus_pro_factures_valideur_rechercher_post,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def valideur_rechercher_factures_api_v1_chorus_pro_factures_valideur_rechercher_post_without_preload_content(
        self,
        body_valideur_rechercher_factures_api_v1_chorus_pro_factures_valideur_rechercher_post: BodyValideurRechercherFacturesApiV1ChorusProFacturesValideurRechercherPost,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Rechercher factures à valider (Valideur)

        Recherche les factures en attente de validation par le valideur connecté.      **Rôle** : Valideur dans le circuit de validation interne.      **Filtres** : Dates, structure, service, etc.

        :param body_valideur_rechercher_factures_api_v1_chorus_pro_factures_valideur_rechercher_post: (required)
        :type body_valideur_rechercher_factures_api_v1_chorus_pro_factures_valideur_rechercher_post: BodyValideurRechercherFacturesApiV1ChorusProFacturesValideurRechercherPost
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._valideur_rechercher_factures_api_v1_chorus_pro_factures_valideur_rechercher_post_serialize(
            body_valideur_rechercher_factures_api_v1_chorus_pro_factures_valideur_rechercher_post=body_valideur_rechercher_factures_api_v1_chorus_pro_factures_valideur_rechercher_post,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _valideur_rechercher_factures_api_v1_chorus_pro_factures_valideur_rechercher_post_serialize(
        self,
        body_valideur_rechercher_factures_api_v1_chorus_pro_factures_valideur_rechercher_post,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if body_valideur_rechercher_factures_api_v1_chorus_pro_factures_valideur_rechercher_post is not None:
            _body_params = body_valideur_rechercher_factures_api_v1_chorus_pro_factures_valideur_rechercher_post


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'HTTPBearer'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/api/v1/chorus-pro/factures/valideur/rechercher',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )




    @validate_call
    def valideur_traiter_facture_api_v1_chorus_pro_factures_valideur_traiter_post(
        self,
        body_valideur_traiter_facture_api_v1_chorus_pro_factures_valideur_traiter_post: BodyValideurTraiterFactureApiV1ChorusProFacturesValideurTraiterPost,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> object:
        """Valider ou refuser une facture (Valideur)

        Valide ou refuse une facture en attente de validation.      **Actions** :     - Valider : La facture passe au statut suivant du circuit     - Refuser : La facture est rejetée (motif obligatoire)

        :param body_valideur_traiter_facture_api_v1_chorus_pro_factures_valideur_traiter_post: (required)
        :type body_valideur_traiter_facture_api_v1_chorus_pro_factures_valideur_traiter_post: BodyValideurTraiterFactureApiV1ChorusProFacturesValideurTraiterPost
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._valideur_traiter_facture_api_v1_chorus_pro_factures_valideur_traiter_post_serialize(
            body_valideur_traiter_facture_api_v1_chorus_pro_factures_valideur_traiter_post=body_valideur_traiter_facture_api_v1_chorus_pro_factures_valideur_traiter_post,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        ).data


    @validate_call
    def valideur_traiter_facture_api_v1_chorus_pro_factures_valideur_traiter_post_with_http_info(
        self,
        body_valideur_traiter_facture_api_v1_chorus_pro_factures_valideur_traiter_post: BodyValideurTraiterFactureApiV1ChorusProFacturesValideurTraiterPost,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> ApiResponse[object]:
        """Valider ou refuser une facture (Valideur)

        Valide ou refuse une facture en attente de validation.      **Actions** :     - Valider : La facture passe au statut suivant du circuit     - Refuser : La facture est rejetée (motif obligatoire)

        :param body_valideur_traiter_facture_api_v1_chorus_pro_factures_valideur_traiter_post: (required)
        :type body_valideur_traiter_facture_api_v1_chorus_pro_factures_valideur_traiter_post: BodyValideurTraiterFactureApiV1ChorusProFacturesValideurTraiterPost
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._valideur_traiter_facture_api_v1_chorus_pro_factures_valideur_traiter_post_serialize(
            body_valideur_traiter_facture_api_v1_chorus_pro_factures_valideur_traiter_post=body_valideur_traiter_facture_api_v1_chorus_pro_factures_valideur_traiter_post,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        response_data.read()
        return self.api_client.response_deserialize(
            response_data=response_data,
            response_types_map=_response_types_map,
        )


    @validate_call
    def valideur_traiter_facture_api_v1_chorus_pro_factures_valideur_traiter_post_without_preload_content(
        self,
        body_valideur_traiter_facture_api_v1_chorus_pro_factures_valideur_traiter_post: BodyValideurTraiterFactureApiV1ChorusProFacturesValideurTraiterPost,
        _request_timeout: Union[
            None,
            Annotated[StrictFloat, Field(gt=0)],
            Tuple[
                Annotated[StrictFloat, Field(gt=0)],
                Annotated[StrictFloat, Field(gt=0)]
            ]
        ] = None,
        _request_auth: Optional[Dict[StrictStr, Any]] = None,
        _content_type: Optional[StrictStr] = None,
        _headers: Optional[Dict[StrictStr, Any]] = None,
        _host_index: Annotated[StrictInt, Field(ge=0, le=0)] = 0,
    ) -> RESTResponseType:
        """Valider ou refuser une facture (Valideur)

        Valide ou refuse une facture en attente de validation.      **Actions** :     - Valider : La facture passe au statut suivant du circuit     - Refuser : La facture est rejetée (motif obligatoire)

        :param body_valideur_traiter_facture_api_v1_chorus_pro_factures_valideur_traiter_post: (required)
        :type body_valideur_traiter_facture_api_v1_chorus_pro_factures_valideur_traiter_post: BodyValideurTraiterFactureApiV1ChorusProFacturesValideurTraiterPost
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :type _request_timeout: int, tuple(int, int), optional
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the
                              authentication in the spec for a single request.
        :type _request_auth: dict, optional
        :param _content_type: force content-type for the request.
        :type _content_type: str, Optional
        :param _headers: set to override the headers for a single
                         request; this effectively ignores the headers
                         in the spec for a single request.
        :type _headers: dict, optional
        :param _host_index: set to override the host_index for a single
                            request; this effectively ignores the host_index
                            in the spec for a single request.
        :type _host_index: int, optional
        :return: Returns the result object.
        """ # noqa: E501

        _param = self._valideur_traiter_facture_api_v1_chorus_pro_factures_valideur_traiter_post_serialize(
            body_valideur_traiter_facture_api_v1_chorus_pro_factures_valideur_traiter_post=body_valideur_traiter_facture_api_v1_chorus_pro_factures_valideur_traiter_post,
            _request_auth=_request_auth,
            _content_type=_content_type,
            _headers=_headers,
            _host_index=_host_index
        )

        _response_types_map: Dict[str, Optional[str]] = {
            '200': "object",
            '422': "HTTPValidationError",
        }
        response_data = self.api_client.call_api(
            *_param,
            _request_timeout=_request_timeout
        )
        return response_data.response


    def _valideur_traiter_facture_api_v1_chorus_pro_factures_valideur_traiter_post_serialize(
        self,
        body_valideur_traiter_facture_api_v1_chorus_pro_factures_valideur_traiter_post,
        _request_auth,
        _content_type,
        _headers,
        _host_index,
    ) -> RequestSerialized:

        _host = None

        _collection_formats: Dict[str, str] = {
        }

        _path_params: Dict[str, str] = {}
        _query_params: List[Tuple[str, str]] = []
        _header_params: Dict[str, Optional[str]] = _headers or {}
        _form_params: List[Tuple[str, str]] = []
        _files: Dict[
            str, Union[str, bytes, List[str], List[bytes], List[Tuple[str, bytes]]]
        ] = {}
        _body_params: Optional[bytes] = None

        # process the path parameters
        # process the query parameters
        # process the header parameters
        # process the form parameters
        # process the body parameter
        if body_valideur_traiter_facture_api_v1_chorus_pro_factures_valideur_traiter_post is not None:
            _body_params = body_valideur_traiter_facture_api_v1_chorus_pro_factures_valideur_traiter_post


        # set the HTTP header `Accept`
        if 'Accept' not in _header_params:
            _header_params['Accept'] = self.api_client.select_header_accept(
                [
                    'application/json'
                ]
            )

        # set the HTTP header `Content-Type`
        if _content_type:
            _header_params['Content-Type'] = _content_type
        else:
            _default_content_type = (
                self.api_client.select_header_content_type(
                    [
                        'application/json'
                    ]
                )
            )
            if _default_content_type is not None:
                _header_params['Content-Type'] = _default_content_type

        # authentication setting
        _auth_settings: List[str] = [
            'HTTPBearer'
        ]

        return self.api_client.param_serialize(
            method='POST',
            resource_path='/api/v1/chorus-pro/factures/valideur/traiter',
            path_params=_path_params,
            query_params=_query_params,
            header_params=_header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            auth_settings=_auth_settings,
            collection_formats=_collection_formats,
            _host=_host,
            _request_auth=_request_auth
        )


